(docker ps | grep myschema) && docker kill myschema
docker run --name myschema --rm -d  -p 8888:8888 -v d:/data/schema:/data myschema