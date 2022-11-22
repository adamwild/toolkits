use minecraft_history::ThreadPool;

use std::{
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};

const ADDRESS: &str = "127.0.0.1:7878";
const OK_STATUS: &str = "HTTP/1.1 200 OK";
const HTML_FILE: &str = include_str!("hello.html");

fn main() {
    let listener = TcpListener::bind(ADDRESS).unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf = BufReader::new(&mut stream);

    // let http_request: Vec<_> = buf
    //     .lines()
    //     .map(|result| result.unwrap())
    //     .take_while(|line| !line.is_empty())
    //     .collect();
    // println!("Request: {:#?}", http_request);
    // this code returns:
    // [
    //     "GET /plop/plouf/plip HTTP/1.1",
    //     "Host: 127.0.0.1:7878",
    //     "User-Agent: curl/7.86.0",
    //     "Accept: */*",
    // ]
    // but in reality only the first line is interesting
    let first_list = buf.lines().next().unwrap().unwrap();
    let (status_line, file_content) = match &first_list[..] {
        "GET / HTTP/1.1" => (OK_STATUS, HTML_FILE),
        _ => ("HTTP/1.1 404 NOT FOUND", "not found"),
    };

    let len = file_content.len();
    let response = format!("{status_line}\r\nContent-Length: {len}\r\n\r\n{file_content}");

    stream.write_all(response.as_bytes()).unwrap();
}
