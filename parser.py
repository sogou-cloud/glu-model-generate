#!/usr/bin/env python2.7
# Style based on: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
# Exception: 100 characters width.

import copy
import json
import os
import sys
import yaml
from collections import defaultdict

def get_agents_in_fabric(entries):
    infos = {}
    install = defaultdict(list)
    tags = defaultdict(list)

    for entry in entries:
        agents = entry['agent']
        sIndex = agents.find('[')
        eIndex = agents.rfind(']')
        arr = []
        if(sIndex !=-1 and eIndex !=-1):
            prefix = agents[:sIndex]
            suffix = agents[eIndex+1:]
            region = agents[sIndex+1:eIndex]
            a, b = region.split('-')
            width = len(a)
            padding = False

            if(len(a) == len(b)):
                padding = True
            for i in range(int(a),int(b)+1):
                arr.append(prefix+str(i).zfill(width)+suffix)
        else:
            arr.append(agents)

        for agent in arr:
            install[agent]+=entry['install']
            tags[agent]+=entry['tags']
    infos['tags'] = tags
    infos['install'] = install
    return infos
def get_model_entry(index, agent, app, builds):
    entry = copy.deepcopy(builds[app])
    entry['agent'] = agent
    entry['mountPoint'] = entry['mountPoint'] % index
    return entry

def get_new_model(cluster):
    fabric = cluster['fabric']
    builds = cluster['apps']
    infos = get_agents_in_fabric(cluster['entries'])
    entries = []
    index = 0
    for (agent,install) in infos['install'].items():
        for app in set(install):
            entries.append(get_model_entry(index, agent, app, builds))
        index += 1
    fabric = {
        'fabric': fabric,
        'entries': entries,
        'agentTags': infos['tags'],
        'metadata': {
            'name': 'Generated model for fabric %s' % fabric
        }
    }
    return fabric


def print_json_dict(dictionary):
    print json.dumps(dictionary, sort_keys=True, indent=4)


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: input cluser describe yaml\n")
        return 1
    cluster = yaml.load(open(argv[1]));
    fabric = cluster['fabric']
    new_model = get_new_model(cluster)
    print_json_dict(new_model)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
