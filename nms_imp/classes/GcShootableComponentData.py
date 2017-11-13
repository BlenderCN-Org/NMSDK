# GcShootableComponentData struct

from .Struct import Struct
from .GcProjectileImpactType import GcProjectileImpactType

STRUCTNAME = 'GcShootableComponentData'

class GcShootableComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcShootableComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Health'] = kwargs.get('Health', 200)
        self.data['AutoAimTarget'] = kwargs.get('AutoAimTarget', False)
        self.data['PlayerOnly'] = kwargs.get('PlayerOnly', False)
        self.data['ImpactShake'] = kwargs.get('ImpactShake', True)
        self.data['ImpactShakeEffect'] = kwargs.get('ImpactShakeEffect', "SHOOTABLESHAKE")
        self.data['ForceImpactType'] = kwargs.get('ForceImpactType', GcProjectileImpactType())
        self.data['IncreaseWanted'] = kwargs.get('IncreaseWanted', 0)
        self.data['IncreaseWantedThresholdTime'] = kwargs.get('IncreaseWantedThresholdTime', 0.5)
        self.data['UseMiningDamage'] = kwargs.get('UseMiningDamage', False)
        self.data['MinDamage'] = kwargs.get('MinDamage', 0)
        self.data['StaticUntilShot'] = kwargs.get('StaticUntilShot', False)
        self.data['RequiredTech'] = kwargs.get('RequiredTech', "")
        """ End of the struct contents"""

        # Parent needed so that it can be a SubElement of something
        self.parent = None
        self.STRUCTNAME = STRUCTNAME