use lazy_static::lazy_static;
use regex::Regex;
use serde::Deserialize;
use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::path::Path;
use std::process::Command;

static WORKSPACE_ROOT: &str = "/home/seb/workspace";
static PRE_COMMIT_FILE: &str = ".pre-commit-config.yaml";
static GIT_DIR: &str = ".git";

/// part of the yaml file containing pre-commit conf
#[derive(Debug, Deserialize, Eq, PartialEq)]
struct PreCommitRepo {
    repo: String,
    rev: String,
}

/// Deserialized version of the pre-commit configuration file
#[derive(Debug, Deserialize, Eq, PartialEq)]
struct PreCommitConfig {
    repos: Vec<PreCommitRepo>,
}

/// main data structure used in this script :
/// path of the pre-commit file and content of the pre-commit file
#[derive(Debug, Deserialize, Eq, PartialEq)]
struct PreCommitFile {
    path: String,
    content: PreCommitConfig,
}

impl Ord for PreCommitFile {
    fn cmp(&self, other: &Self) -> Ordering {
        self.content.repos.len().cmp(&other.content.repos.len())
    }
}

impl PartialOrd for PreCommitFile {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// find all .pre-commit-config.yaml file
/// start the exploration in the workspace directory. Explore recursively each folder
/// for each folder :
/// - if a file `.pre-commit-config.yaml` is present, stop the exploration
/// - if a file .git is present, don't go in sub-directory
/// - else continue the exploration to all sub-folder
fn find_pre_commit_config() -> Result<Vec<String>, Box<dyn Error>> {
    let mut folders_to_explore: Vec<String> = vec![WORKSPACE_ROOT.to_string()];
    let mut all_pre_commit_files = Vec::new();
    while let Some(f) = folders_to_explore.pop() {
        let mut continue_explo = true;
        let mut new_folders_to_explore = Vec::new();
        for f in fs::read_dir(f)?.map(|v| v.unwrap()) {
            if f.file_type()?.is_dir() {
                if f.file_name() == GIT_DIR {
                    continue_explo = false;
                } else {
                    new_folders_to_explore.push(f.path().into_os_string().into_string().unwrap());
                }
            } else if f.file_name() == PRE_COMMIT_FILE {
                all_pre_commit_files.push(f.path().into_os_string().into_string().unwrap());
                continue_explo = false;
                break;
            }
        }
        if continue_explo {
            folders_to_explore.append(&mut new_folders_to_explore)
        }
    }
    Ok(all_pre_commit_files)
}

fn run_pre_commit_autoupdate(path: &Path) {
    let output = Command::new("sh")
        .arg("-c")
        .arg(format!(
            "cd {} && pre-commit autoupdate",
            path.to_str().unwrap()
        ))
        .output()
        .expect("failed to execute process");
    println!("status: {}", output.status);
    println!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    println!("stderr: {}", String::from_utf8_lossy(&output.stderr));
}

fn main() -> Result<(), Box<dyn Error>> {
    let all_pre_commit_files = find_pre_commit_config()?;

    // find all repo use in all pre_commit files
    let mut heap = BinaryHeap::new();
    for path in all_pre_commit_files.into_iter() {
        let content = fs::read_to_string(&path)?;
        let content: PreCommitConfig = serde_yaml::from_str(&content)?;
        heap.push(PreCommitFile { content, path })
    }

    let mut updated_hooks = HashMap::new();
    while let Some(pcc) = heap.pop() {
        println!(
            "\n# Process {}:\n  - {} hooks",
            pcc.path,
            pcc.content.repos.len()
        );
        let mut need_run_autoupdate = false;
        let mut pcc_content = fs::read_to_string(&pcc.path)?;

        for hooks in pcc.content.repos {
            if updated_hooks.contains_key(&hooks.repo) {
                // manually update
                let repo_name = hooks.repo.split("/").last().unwrap();

                // lazy_static! {
                // static ref re: Regex = Regex::new(
                //     &format!("{}(?:rep[^o]|re[^p]|r[^e]|[^r])*rev: ([^\n]+)(?:rep[^o]|re[^p]|r[^e]|[^r])*")
                //     ).unwrap();
                // }
                let re: Regex = Regex::new(&format!(
                    "(?P<b>{}(?:rep[^o]|re[^p]|r[^e]|[^r])*rev:) ([^\n]+)(?P<a>(?:rep[^o]|re[^p]|r[^e]|[^r])*)",
                    repo_name
                ))
                .unwrap();

                pcc_content = re
                    .replace(
                        &pcc_content,
                        format!("$b {}$a", updated_hooks.get(&hooks.repo).unwrap()),
                    )
                    .to_mut()
                    .clone();
            } else {
                need_run_autoupdate = true;
                break;
            }
        }

        if need_run_autoupdate {
            // update pre-commit config
            let path = Path::new(&pcc.path);
            run_pre_commit_autoupdate(path.parent().unwrap());

            // update updated_hooks
            let content = fs::read_to_string(&pcc.path)?;
            let updated_pcc: PreCommitConfig = serde_yaml::from_str(&content)?;

            for repo in updated_pcc.repos.into_iter() {
                if !updated_hooks.contains_key(&repo.repo) {
                    println!("new repo : {}", &repo.repo);
                    updated_hooks.insert(repo.repo, repo.rev);
                }
            }
        } else {
            println!("  - automatic update performed");

            // copy file
            let dest_path = format!(
                "{}/perso_pre_commit_config_save.yaml",
                Path::new(&pcc.path).parent().unwrap().to_str().unwrap()
            );
            println!("    - move to {}", dest_path);
            fs::copy(&pcc.path, &dest_path)?;
            // save new version
            fs::write(&pcc.path, &pcc_content)?;
        }
    }

    Ok(())
}
