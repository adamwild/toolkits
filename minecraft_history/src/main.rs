use std::{
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};

const ADDRESS: &str = "127.0.0.1:7878";
const STATUS_LINE: &str = "HTTP/1.1 200 OK";
const LENGTH: usize = HTML_FILE.len();
const HTML_FILE: &str = include_str!("hello.html");

fn main() {
    let listener = TcpListener::bind(ADDRESS).unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();
        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf = BufReader::new(&mut stream);
    let http_request: Vec<_> = buf
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();

    println!("Request: {:#?}", http_request);

    // let length = HTML_FILE.len();

    let response = format!("{STATUS_LINE}\r\nContent-Length: {LENGTH}\r\n\r\n{HTML_FILE}");

    stream.write_all(response.as_bytes()).unwrap();
}
