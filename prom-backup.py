import logging
import requests
import sys
from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL

def main():
    if len(sys.argv) < 3:
        print("Usage: " + sys.argv[0] + " <snapshot_prefix> <max_snapshot_age_in_min_to_retain> <prom_url>")
        print("NOTE: snapshots older than <max_snapshot_age_in_min_to_retain> with prefix <snapshot_prefix> will be deleted.")
        sys.exit()

    # Create snapshot
    prefix = sys.argv[1]
    max_age_min = sys.argv[2]
    prom_url = sys.argv[3]
    response = None
    try:
        response = requests.post(prom_url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)

    if response.ok:
        print("Snapshot response was OK")
    else:
        sys.exit("Snapshot response was NOT OK")

    print("Status code = " + str(response.status_code))
    snapshot_name = response.json()['data']['name']

    # Compress snapshot into g-zipped tar archive
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    exec_command = [
        '/bin/sh',
        '-c',
        "/bin/tar zcvf /prometheus/snapshots/" + prefix + snapshot_name + ".tgz /prometheus/snapshots/" + snapshot_name]

    sclient = stream(v1.connect_get_namespaced_pod_exec,
                     'prometheus-tartarus-prometheus-0',
                     'monitoring',
                     container='prometheus',
                     command=exec_command,
                     stderr=True, stdin=False,
                     stdout=True, tty=False,
                     _preload_content=False)

    sclient.run_forever()

    if sclient.returncode == 0:
        print("Tar archive created successfully")
    else:
        err = sclient.read_channel(ERROR_CHANNEL)
        sys.exit(yaml.load(err))

    # Delete snapshot directory
    dir = "/prometheus/snapshots/" + snapshot_name
    exec_command = [
        '/bin/sh',
        '-c',
        "/bin/rm -rf " + dir]

    sclient = stream(v1.connect_get_namespaced_pod_exec,
                     'prometheus-tartarus-prometheus-0',
                     'monitoring',
                     container='prometheus',
                     command=exec_command,
                     stdout=True, tty=False,
                     _preload_content=False)

    sclient.run_forever() 

    if sclient.returncode == 0: 
        print("Snapshot directory deleted")
    else: 
        err = sclient.read_channel(ERROR_CHANNEL)
        sys.exit(yaml.load(err))

    # Delete old snapshot files
    exec_command = [
        '/bin/sh',
        '-c',
#        "/bin/find /prometheus/snapshots/" + prefix "*tgz -mtime +" + max_age_days + " -exec rm {} \;"]
        "/bin/find /prometheus/snapshots/" + prefix + "*tgz -mmin +" + max_age_min + " -exec rm {} \;"]

    sclient = stream(v1.connect_get_namespaced_pod_exec,
                     'prometheus-tartarus-prometheus-0',
                     'monitoring',
                     container='prometheus',
                     command=exec_command,
                     stderr=True, stdin=False,
                     stdout=True, tty=False,
                     _preload_content=False)

    sclient.run_forever()

    if sclient.returncode == 0:
        print("Command to delete old snapshot tar archives was successful")
    else:
        err = sclient.read_channel(ERROR_CHANNEL)
        sys.exit(yaml.load(err))

if __name__ == '__main__':
    main()
