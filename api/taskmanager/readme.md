```
docker build . --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/taskmanager:latest
```

```
docker push us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/taskmanager:latest
```

```
gcloud run deploy taskmanager --image us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/taskmanager:latest --region us-central1
```


```
gcloud builds submit --tag us-central1-docker.pkg.dev/cloud-w3-403103/cloud-run-source-deploy/taskmanager:latest
```