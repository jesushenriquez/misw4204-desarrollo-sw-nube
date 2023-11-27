```
docker build . --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/authcomponent:latest
```

```
docker push us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/authcomponent:latest
```

```
gcloud run deploy authcomponent --image us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/authcomponent:latest --region us-central1
```


```
gcloud builds submit --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/authcomponent:latest
```