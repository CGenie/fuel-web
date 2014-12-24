import copy
import json
import random
import tempfile

temp_file = None

IPS = set()
MACS = set()


class FakeNode(object):
    id = None
    name = None
    meta = None
    progress = None
    roles = None
    pending_roles = None
    status = None
    mac = None
    fqdn = None
    ip = None
    manufacturer = None
    platform_name = None
    pending_addition = None
    pending_deletion = None
    os_platform = None
    error_type = None
    online = None
    cluster = None
    uuid = None
    network_data = None
    group_id = None
    kernel_params = None
    grouping = None


node_template = {
    "pk": 2,
    "model": "nailgun.node",
    "fields": {
        "status": "discover",
        "name": "Dell Inspiron",
        "ip": "10.20.0.1",
        "online": True,
        "pending_addition": False,
        "platform_name": "Inspiron N5110",
        "mac": "58:91:cF:2a:c4:1b",
        "meta": {
            "memory": {
                "slots": 2,
                "total": 8589934592,
                "maximum_capacity": 17179869184,
                "devices": [
                    {
                        "frequency": 1333,
                        "type": "DDR3",
                        "size": 4294967296
                    },
                    {
                        "frequency": 1333,
                        "type": "DDR3",
                        "size": 4294967296
                    }
                ]
            },
            "interfaces": [],
            "disks": [
                {
                    "model": "Silicon-Power16G",
                    "name": "sdb",
                    "disk": "sdb",
                    "size": 15518924800
                },
                {
                    "model": "WDC WD3200BPVT-7",
                    "name": "sda",
                    "disk": "sda",
                    "size": 320072933376
                }
            ],
            "system": {
                "product": "Inspiron N5110",
                "serial": "044ED881",
                "fqdn": "lab-10",
                "manufacturer": "80AD"
            },
            "cpu": {
                "real": 1,
                "total": 8,
                "spec": [
                    {
                        "model": "Intel(R) Core(TM) i7-2670QM CPU @ 2.20GHz",
                        "frequency": 2201
                    },
                ]*8
            }
        },
        "timestamp": "",
        "progress": 0,
        "pending_deletion": False,
        "os_platform": "ubuntu",
        "manufacturer": "80AD"
    }
}


def generate_random_ip(netmask=(192, 168)):
    while True:
        ip = (netmask[0], netmask[1], random.randint(0, 255), random.randint(0, 255))
        if ip not in IPS:
            IPS.add(ip)
            break
    return ip


def generate_random_mac():
    while True:
        mac = [random.randint(0x00, 0x7f) for _ in xrange(6)]
        ret = ':'.join(map(lambda x: "%02x" % x, mac)).lower()
        if ret not in MACS:
            MACS.add(ret)
            break
    return ret


def generate_interfaces(num=4):
    ifc_template = {
        "ip": "192.168.70.234",
        "mac": "24:b6:fd:53:63:00",
        "max_speed": 100,
        "name": "eth0",
        "current_speed": 10,
    }

    ret = []

    for i in range(num):
        ifc = copy.deepcopy(ifc_template)
        ifc['ip'] = generate_random_ip()
        ifc['mac'] = generate_random_mac()
        ifc['name'] = 'eth%d' % i
        ret.append(ifc)

    return ret


def generate_node():
    ret = copy.deepcopy(node_template)

    ret['fields']['ip'] = generate_random_ip((10, 20))
    ret['fields']['mac'] = generate_random_mac()
    ret['fields']['meta']['interfaces'] = generate_interfaces()

    return ret


def generate_sample_environment_fixture():
    global temp_file

    temp_file = tempfile.TemporaryFile()

    r = []
    for i in range(100):
        node = generate_node()
        node['pk'] = i
        node['fields']['name'] = '%s %d' % (node['fields']['name'], i)
        r.append(node)

    temp_file.write(json.dumps(r, indent=2))


def generate_fake_node(node_dict):
    fake_node = FakeNode()
    for k, v in node_dict.items():
        setattr(fake_node, k, v)
    for k, v in node_dict['fields'].items():
        setattr(fake_node, k, v)
    fake_node.id = fake_node.pk
    fake_node.kernel_params = None
    fake_node.pending_addition = False
    fake_node.pending_deletion = False
    fake_node.pending_roles = []
    fake_node.roles = []
    fake_node.grouping = 'hardware'

    return fake_node


def get_sample_environment():
    if temp_file is None:
        generate_sample_environment_fixture()

    temp_file.seek(0)

    nodes = json.loads(temp_file.read())

    ret = []

    for node in nodes:
        ret.append(generate_fake_node(node))

    return ret
