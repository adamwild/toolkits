// load a yaml file with
// - a dict `pnj` pnj_name => pnj_picture
// - folder to load images from
// - number of columns to make
use fast_image_resize as fr;
use fr::Resizer;
use image::imageops::{replace, rotate180_in_place};
use image::io::Reader as ImageReader;
use image::{ImageBuffer, Rgb, RgbImage};
use imageproc::drawing::draw_text_mut;
use ordered_float::OrderedFloat;
use rayon::prelude::*;
use rusttype::Font;
use rusttype::Scale;
use serde::Deserialize;
use std::cmp::min;
use std::num::NonZeroU32;
use std::{collections::HashMap, fs, time};

#[derive(Deserialize, Debug)]
struct ConfFile {
    pnj: HashMap<String, String>,
    folder: String,
    n_col: u8,
}

fn resize(
    img: ImageBuffer<Rgb<u8>, Vec<u8>>,
    ratio: f64,
    resizer: &mut fr::Resizer,
) -> ImageBuffer<Rgb<u8>, Vec<u8>> {
    let width = img.width();
    let height = img.height();
    let src_image = fr::Image::from_vec_u8(
        NonZeroU32::new(width).unwrap(),
        NonZeroU32::new(height).unwrap(),
        img.into_raw(),
        fr::PixelType::U8x3,
    )
    .unwrap();

    // Create container for data of destination image
    let dst_height = (height as f64 * ratio) as u32;
    let dst_width = (width as f64 * ratio) as u32;
    let mut dst_image = fr::Image::new(
        NonZeroU32::new(dst_width).unwrap(),
        NonZeroU32::new(dst_height).unwrap(),
        src_image.pixel_type(),
    );
    let mut dst_view = dst_image.view_mut();
    resizer.resize(&src_image.view(), &mut dst_view).unwrap();

    RgbImage::from_raw(dst_width, dst_height, dst_image.into_vec()).unwrap()
}

fn load_and_prepare_image(
    image_path: String,
    resizer: &mut Resizer,
    w_pixel: u32,
    h_pixel: u32,
) -> ImageBuffer<Rgb<u8>, Vec<u8>> {
    let mut image = ImageReader::open(image_path)
        .unwrap()
        .decode()
        .unwrap()
        .to_rgb8();

    // rotate 180°
    rotate180_in_place(&mut image);
    // resize
    let ratio = min(
        OrderedFloat((w_pixel as f64) / (image.width() as f64)),
        OrderedFloat((h_pixel as f64) / (image.height() as f64)),
    )
    .0;
    resize(image, ratio, resizer)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let t = time::Instant::now();
    println!("Parse configuration file");
    let yaml_file = "conf.yaml";
    let yaml_content = fs::read_to_string(&yaml_file)?;
    let conf_file: ConfFile = serde_yaml::from_str(&yaml_content)?;
    println!("{:#?}", &conf_file);
    println!("load conf: {:?}", t.elapsed());


    let t = time::Instant::now();
    let full_image_h = 29.7;
    let full_image_w = 21.;

    let n_col = conf_file.n_col;
    let n_pnj = conf_file.pnj.len();
    let n_lignes = (n_pnj as f64 / n_col as f64).ceil();

    let small_image_h = full_image_h / (2. * n_lignes);
    let small_image_w = full_image_w / (n_col as f64);

    let w_pixel: u32 = 250;
    let h_pixel = (w_pixel as f64 * small_image_h / small_image_w).ceil() as u32;

    let full_image_h = ((h_pixel as f64) * 2. * n_lignes) as i32;
    let full_image_w = w_pixel * (n_col as u32);

    let font_data: &[u8] = include_bytes!("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf");
    let font: Font<'static> = Font::try_from_bytes(font_data).unwrap();
    println!("init all vars: {:?}", t.elapsed());

    // create white image
    let t = time::Instant::now();
    let mut img = RgbImage::from_pixel(
        full_image_w as u32,
        full_image_h as u32,
        Rgb([255, 255, 255]),
    );
    println!("create white image: {:?}", t.elapsed());

    let t = time::Instant::now();
    let resizer = fr::Resizer::new(fr::ResizeAlg::Convolution(fr::FilterType::Bilinear));
    let pnj_images: Vec<(String, ImageBuffer<Rgb<u8>, Vec<u8>>)> = conf_file
        .pnj
        .into_par_iter()
        .map(|(pnj_name, pnj_path)| {
            (
                pnj_name,
                load_and_prepare_image(
                    conf_file.folder.clone() + &pnj_path,
                    &mut resizer.clone(),
                    w_pixel,
                    h_pixel,
                ),
            )
        })
        .collect();
    println!("load and process images: {:?}", t.elapsed());

    let t = time::Instant::now();
    for (i, (pnj_name, pnj_picture)) in pnj_images.into_iter().enumerate() {
        // update global image
        let image_position_x = (i as i64 % (n_col as i64)) * w_pixel as i64;
        let image_position_y = (i as i64 / (n_col as i64)) * h_pixel as i64 * 2;
        replace(&mut img, &pnj_picture, image_position_x, image_position_y);

        // add text
        let text_size = 35.;
        for (i, text) in pnj_name.split(" ").enumerate() {
            draw_text_mut(
                &mut img,
                Rgb([0, 0, 0]),
                image_position_x as i32,
                (image_position_y + 500 + (i as i64) * 30) as i32,
                Scale {
                    x: text_size,
                    y: text_size,
                },
                &font,
                text,
            )
        }
    }
    println!("update main image: {:?}", t.elapsed());

    let t = time::Instant::now();
    img.save("/tmp/tmp.png")?;
    println!("save image: {:?}", t.elapsed());

    Ok(())
}
