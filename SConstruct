#!/usr/bin/python
#
# At the moment theres a big hack on autoinclude of SConscripts files
# So for now you NEED to:
#
# To BUILD targets:
#  mkdir BUILD
#  cd BUILD
#  scons -Y .. <targetlist>
#
# To clean:
#  cd BUILD
#  scons -c

import os

def ListAllBuildScripts():
  '''List all build scripts available.
  
  At the moment it walks thorugh the filesytem tree and adds all SConscripts.
  Its only a temporary replacement till I find time to code a version that goes
  through the Scons tree.'''
  def iterBuildScripts(path):
    for [root, dirs, files] in os.walk(path):
      if 'SConscript' in files:
        filename = os.path.join(root, 'SConscript')
        yield filename[3:]
      for dir in dirs:
        for bs in iterBuildScripts(os.path.join(root, 'dir')):
          yield bs
  return list(iterBuildScripts('..'))


BS = ListAllBuildScripts()
print('Automaticaly including the scripts:', BS)
SConscript(BS)
