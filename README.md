# kubernetes-file-backup

This repository will contain a Go program for copying a file out of a Kubernetes pod running in the same cluster. The helm chart in this repo will be tested on an Azure Kubernetes Service (AKS) cluster and use an Azure Blob Storage volume for storing file backups, but the same application could be used (with a modified helm chart) on any Kubernetes cluster.

The purpose of backing up individual files from a pod running in Kubernetes is for operating applications like Prometheus that are designed to generate a snapshot on their local file system when an admin sends an HTTP request to the Prometheus admin API. This approach could also be used to backup Elasticsearch snapshots. However, Elasticsearch also has built-in support for sending snapshots to cloud storage providers, whereas Prometheus currently does not.

This repository will include the following:
- Golang application for copying files from a pod in the cluster to a locally mounted file system
- Dockerfile to compile and run our application
- Helm chart to deploy the application as a Kubernetes CronJob

The helm chart will include the following:
- Persistent Volume to mount an Azure Blob for storing our file backups
- Service Account token to allow our application to access another pod in the cluster
- Dynamically generated CronJobs for running each of the backup schedules defined in our values.yaml
- Options for the list of pod files to backup, their backup schedule, where to store them, and whether to delete the source files after backup
