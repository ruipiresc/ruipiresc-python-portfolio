import os
import sys

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'portfolio', '__version__.py')) as f:
    exec(f.read(), about)

if len(sys.argv) > 1:
    if sys.argv[1] == 'tag':
        option = 'build'
        if len(sys.argv) > 2:
            if sys.argv[2] == 'patch':
                option = 'patch'
            elif sys.argv[2] == 'minor':
                option = 'minor'
            elif sys.argv[2] == 'major':
                option = 'major'
            elif sys.argv[2] == 'release':
                option = 'release'
        if option == 'build' and 'dev' not in about['__version__']:
            raise ValueError('cannot tag a build without starting a patch, minor or major update')
        os.system('python -m bumpversion ' + option)
        os.system('git push')
        os.system('git push --tags')
        sys.exit()

with open('README.md', 'r') as f:
    readme = f.read()
