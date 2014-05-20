import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    Video,
    Base,
    User
    )

from ..DBHelper import DBSession


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    

    with transaction.manager:
        #add entries to database here
        user = User(handler="son", password="123123")
        DBSession.add(user)
        for i in range(0,100):
            video = Video(title="AMAZING STREET HACK", url="https://www.youtube.com/watch?v=1hpU_Neg1KA",
                owner=user, description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla in hendrerit odio, sed venenatis lectus. Aenean placerat, justo id porttitor faucibus, sem lorem imperdiet odio, a vehicula risus nisi varius leo. Nulla imperdiet nunc fringilla imperdiet venenatis. Nullam eu mi cursus, consequat ipsum et, sodales arcu. In fermentum molestie leo in sed. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla in hendrerit odio, sed venenatis lectus. Aenean placerat, justo id porttitor faucibus, sem lorem imperdiet odio, a vehicula risus nisi varius leo. Nulla imperdiet nunc fringilla imperdiet venenatis. Nullam eu mi cursus, consequat ipsum et, sodales arcu. In fermentum molestie leo in sed.")
            DBSession.add(video)
        pass
