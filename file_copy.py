import requests
from kubernetes import client, config

def main():
    prom_url = 'http://tartarus-prometheus.monitoring.svc.cluster.local:9090/api/v1/admin/tsdb/snapshot'
    response = None
    try:
        response = requests.post(prom_url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)

    if response.ok:
        print("Response was OK")
    else:
        print("Response was not OK")

    print("Status code = " + str(response.status_code))

    config.load_incluster_config()

    v1 = client.CoreV1Api()

    exec_command = [
        '/bin/sh',
        '-c',
        '/bin/ls /prometheus/snapshots']

    resp = stream(v1.connect_get_namespaced_pod_exec,
                  'prometheus-tartarus-prometheus-0',
                  'monitoring',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)

if __name__ == '__main__':
    main()
