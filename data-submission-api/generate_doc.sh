docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli:latest generate -i /local/waterly-connect.yml -g html2 -o /local
