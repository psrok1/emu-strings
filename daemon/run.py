from gevent.monkey import patch_all
patch_all()

import gevent
from libs.context import AnalysisContext
from fakenet import Fakenet

context = AnalysisContext()

fakenet = Fakenet(context)
fakenet.start()

gevent.spawn(context.analyze).join()

fakenet.shutdown()
