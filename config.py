import yaml

with open('/home/tuba/config.yaml', 'r') as f:
  settings = yaml.load(f)

with open('/home/tuba/emoji.yaml', 'r') as f:
  emojis = yaml.load(f)

def colorPick(r,g,b):
  return (r*65536) + (g*256) + b
