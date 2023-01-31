import file_manager
import hashlib
import logging
import requests
import tarfile
import traceback
from kubernetes import client, config
from kubernetes.stream import stream
from tempfile import TemporaryFile

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
    snapshot_name = response.json()['data']['name']

    config.load_incluster_config()

    v1 = client.CoreV1Api()

    exec_command = [
        '/bin/sh',
        '-c',
        "/bin/tar zcvf /prometheus/snapshots/" + snapshot_name + ".tgz /prometheus/snapshots/" + snapshot_name]

    resp = stream(v1.connect_get_namespaced_pod_exec,
                  'prometheus-tartarus-prometheus-0',
                  'monitoring',
                  container='prometheus',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)

    fp = "/prometheus/snapshots/" + snapshot_name + ".tgz"

    exec_command = [
        '/bin/sh',
        '-c',
        "/bin/md5sum " + fp]

    resp = stream(v1.connect_get_namespaced_pod_exec,
                  'prometheus-tartarus-prometheus-0',
                  'monitoring',
                  container='prometheus',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    md5sum = resp.split(maxsplit = 1)[0]

    dest_path = "/tmp/" + snapshot_name + ".tgz"
    command_copy = ['tar', 'cf', '-', fp]
    with TemporaryFile() as tar_buffer:
        exec_stream = stream(v1.connect_get_namespaced_pod_exec,
                             'prometheus-tartarus-prometheus-0',
                             'monitoring',
                             container='prometheus',
                             command=command_copy, stderr=True, stdin=True, stdout=True, tty=False,
                             _preload_content=False)
        # Copy file to stream
        try:
            reader = file_manager.WSFileManager(exec_stream)
            while True:
                out, err, closed = reader.read_bytes()
                if out:
                    tar_buffer.write(out)
                elif err:
                    logging.debug("Error copying file {0}".format(err.decode("utf-8", "replace")))
                if closed:
                    break
            exec_stream.close()
            tar_buffer.flush()
            tar_buffer.seek(0)
            with tarfile.open(fileobj=tar_buffer, mode='r:') as tar:
                member = tar.getmember(fp[1:])
                tar.makefile(member, dest_path)
                return True
        except Exception as e:
            logging.error(traceback.format_exc())

    copied_md5sum = hashlib.md5(open(dest_path,'rb').read()).hexdigest()

    if(md5sum == copied_md5sum):
        print("Success!")
    else:
        print("Failed.")

if __name__ == '__main__':
    main()
