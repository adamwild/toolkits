// load a yaml file with
// - a dict `pnj` pnj_name => pnj_picture
// - folder to load images from
// - number of columns to make
use image::imageops::{replace, resize, rotate180_in_place, FilterType};
use image::io::Reader as ImageReader;
use image::{RgbImage, Rgb};
use imageproc::drawing::draw_text_mut;
use ordered_float::OrderedFloat;
use serde::Deserialize;
use std::cmp::min;
use std::{collections::HashMap, fs, time};
use rusttype::Scale;
use rusttype::Font;
use fast_image_resize as fr;

#[derive(Deserialize, Debug)]
struct ConfFile {
    pnj: HashMap<String, String>,
    folder: String,
    n_col: u8,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let t = time::Instant::now();
    println!("Parse configuration file");
    let yaml_file = "conf.yaml";
    let yaml_content = fs::read_to_string(&yaml_file)?;
    let conf_file: ConfFile = serde_yaml::from_str(&yaml_content)?;
    println!("{:#?}", &conf_file);
    println!("parse config file: {:?}", t.elapsed());


    let full_image_h = 29.7;
    let full_image_w = 21.;

    let n_col = conf_file.n_col;
    let n_pnj = conf_file.pnj.len();
    let n_lignes = (n_pnj as f64 / n_col as f64).ceil();

    let small_image_h = full_image_h / (2. * n_lignes);
    let small_image_w = full_image_w / (n_col as f64);

    let w_pixel = 250;
    let h_pixel = (w_pixel as f64 * small_image_h / small_image_w).ceil() as i32;

    let full_image_h = ((h_pixel as f64) * 2. * n_lignes) as i32;
    let full_image_w = w_pixel * (n_col as i32);

    // create white image
    let t = time::Instant::now();
    let mut img = RgbImage::from_pixel(full_image_w as u32, full_image_h as u32, Rgb([255,255,255]));
    println!("create white image: {:?}", t.elapsed());

    let font_data: &[u8] = include_bytes!("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf");
    let font: Font<'static> = Font::try_from_bytes(font_data).unwrap();


    let mut load_image_time = time::Duration::ZERO;
    let mut rotate_and_resize_time = time::Duration::ZERO;
    for (i, (pnj_name, png_path)) in conf_file.pnj.iter().enumerate() {
        println!("{}", i);

        // load image
        let t = time::Instant::now();
        let mut pnj_picture = ImageReader::open(conf_file.folder.clone() + png_path)?
            .decode()?
            .to_rgb8();
        load_image_time = load_image_time + t.elapsed();

        // rotate 180°
        // idea : do it inplace ?
        // idea : do rotate and replace in a single function ? (For loop) With SIMD ?
        let t = time::Instant::now();
        rotate180_in_place(&mut pnj_picture);
        // resize
        let ratio = min(
            OrderedFloat((w_pixel as f64) / (pnj_picture.width() as f64)),
            OrderedFloat((h_pixel as f64) / (pnj_picture.height() as f64)),
        )
        .0;
        let pnj_picture = resize(
            &pnj_picture,
            (pnj_picture.width() as f64 * ratio) as u32,
            (pnj_picture.height() as f64 * ratio) as u32,
            FilterType::Triangle,
        );
        rotate_and_resize_time = rotate_and_resize_time + t.elapsed();

        // update global image
        let image_position_x = (i as i64 % (n_col as i64)) * w_pixel as i64;
        let image_position_y = (i as i64 / (n_col as i64)) * h_pixel as i64 * 2;
        replace(
            &mut img,
            &pnj_picture,
            image_position_x,
            image_position_y,
        );
        // image[image_position_y*h_pixel*2:image_position_y*h_pixel*2+img.shape[0],
        //         image_position_x*w_pixel:image_position_x*w_pixel+img.shape[1],
        //         :] = img

        // add text
        let text_size = 35.;
        for (i, text) in pnj_name.split(" ").enumerate(){
            draw_text_mut(
                &mut img,
                Rgb([0,0,0]),
                image_position_x as i32,
                (image_position_y + 500 + (i as i64)*30) as i32,
                Scale { x: text_size, y: text_size }, // scale
                &font,
                text

            )
        }
    }

    println!("load image: {:?}", load_image_time);
    println!("rotate and resize time: {:?}", rotate_and_resize_time);


    img.save("/tmp/tmp.png")?;

    Ok(())
}
