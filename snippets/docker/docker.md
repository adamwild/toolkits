build a static website

```docker
FROM nginx:1.21.6-alpine
COPY --from=builder /opt/site /usr/share/nginx/html
```


start a python env
```sh
docker run -it --rm -v $PWD:/opt -p 8000:8000 python:3.8 bash
```

start a jupyter notebook in docker
```sh
jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --port 8000
```
