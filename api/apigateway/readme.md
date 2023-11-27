```
docker build . --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/apigateway:latest
```

```
docker push us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/apigateway:latest
```

```
❯ gcloud run deploy testapi --image us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/apigateway:latest --region us-central1 
```


```
gcloud builds submit --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/apigateway:latest
```