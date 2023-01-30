import requests
from kubernetes import client, config

def main():
    prom_url = 'http://tartarus-prometheus.monitoring.svc.cluster.local:9090/api/v1/admin/tsdb/snapshot'
    response = None
    try:
        response = requests.post(prom_url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)

    if reponse.ok:
        print response.status_code
    else:
        print "Response was not okay." + status_code

    config.load_incluster_config()

    v1 = client.CoreV1Api()

    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

if __name__ == '__main__':
    main()
