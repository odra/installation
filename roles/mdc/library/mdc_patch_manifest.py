from ansible.module_utils.basic import AnsibleModule

import json


def build():
    return AnsibleModule(
        argument_spec=dict(
            env_var=dict(required=True, type='str'),
            path=dict(required=True, type='str'),
            secret_name=dict(required=True, type='str'),
            dc=dict(required=True, type='dict'),
        ),
        supports_check_mode=True,
    )


def parse(data):
    if isinstance(data, str):
        return json.loads(data)
    return data


def main():
    has_changed = True
    module = build()
    path_parts = module.params['path'].split('/')
    folder = '/'.join(path_parts[:-1])
    fname = path_parts[-1]

    dc = parse(module.params['dc'])
    for container in dc['spec']['template']['spec']['containers']:
        if container['name'] == 'mdc':
            if not 'env' in container:
                container['env'] = []
            container['env'].append({
                'name': module.params['env_var'],
                'value': module.params['path']
            })
            if not 'volumeMounts' in container:
                container['volumeMounts'] = []
            container['volumeMounts'].append({
                'name': module.params['secret_name'],
                'mountPath':folder,
                'readOnly': True,
            })
    if not 'volumes' in dc['spec']['template']['spec']:
        dc['spec']['template']['spec']['volumes'] = []
    dc['spec']['template']['spec']['volumes'].append({
        'name': module.params['secret_name'],
        'secret': {
            'secretName': module.params['secret_name'],
            'items': [
                {
                    'key': 'generated_manifest',
                    'path': fname,
                }
            ]
        }
    })

    module.exit_json(changed=has_changed, data=dc)


if __name__ == '__main__':
    main()