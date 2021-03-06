# Filters to return ec2 related attributes

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
import json
import os
import yaml
import time
import pickle
import boto.ec2
import re

class GetRegion():
  def __init__(self):
    self.cache_dir = os.path.join(os.environ['HOME'],'.stack_resources')
    self.cache_time = 60

  def check_cache(self, file):
    now = int(time.time())
    data = ''
    if os.path.isfile(file):
      # check time stamp of file
      if ( now - int(os.path.getmtime(file)) ) < self.cache_time:
        fh = open(file, 'r')
        data = pickle.load(fh)

    return data

  def get_regions(self):
    regions_cache = os.path.join(self.cache_dir, 'regions')
    regions = self.check_cache(regions_cache)
    if regions:
      pass
    else:
      try:
        regions = boto.ec2.regions()
        regions = [ r.name for r in regions ]
        fh = open(regions_cache, 'w')
        pickle.dump(regions, fh)
      except:
        raise AnsibleError('Couldn\'t retrieve aws regions')

    return regions

# main
def eip_allocid(ip,region=None):
  ec2 = GetRegion()
  regions = ec2.get_regions()

  if region:
    region = region
  else:
    if 'AWS_REGION' in os.environ:
      region = os.environ['AWS_REGION']
    else:
      raise AnsibleError('aws region not found in argument or AWS_REGION env var')

  if not region in regions:
    raise AnsibleError('%s is not a valid aws region' % aws_region)

  ec2 = boto.ec2.connect_to_region(region)

  try:
    eip_allocid = ec2.get_all_addresses(filters={'public-ip': ip})[0].allocation_id
  except Exception, e:
    raise AnsibleError('Couldn\'t retrieve eip allocation id. Error was %s' % str(e))

  m = re.search('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip)
  if not m:
      raise AnsibleError('"%s" is not a valid ip address.' % ip)

  return eip_allocid

class FilterModule(object):
  def filters(self):
    return {
      'eip_allocid' : eip_allocid
    }
