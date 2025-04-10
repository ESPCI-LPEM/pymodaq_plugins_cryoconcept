"""
Created the 20/03/2025

@author: Louis Grandvaux
"""

import numpy as np

from pyqtgraph.parametertree.parameterTypes.basetypes import GroupParameter
from pyqtgraph.parametertree.parameterTypes import registerParameterType

from pymodaq.utils.data import DataFromPlugins
from pymodaq.utils.parameter import Parameter, utils

from pymodaq_data.data import DataToExport

from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq_plugins_cryoconcept.hardware.Cryostat import Cryostat

CHANNELS = ["fr", "still", "stage1", "stage2"]

for channel in CHANNELS:
    assert hasattr(Cryostat, channel)

class ChannelGroup(GroupParameter):
    """Group Parameter listing the different outputs of the MMR3
    """

    def __init__(self, **opts) -> None:
        opts['type'] = 'cryostatchannel'
        opts['addText'] = 'Add channel'
        super().__init__(**opts)

    def addNew(self) -> None:
        """Add new channel to viewer
        """
        name_prefix = "channel"

        child_indexes = [int(par.name()[len(name_prefix) + 1:])
                         for par in self.children()]
        
        if child_indexes == []:
            newindex = 0
        else:
            newindex = max(child_indexes) + 1

        child = {
            'title': f'Measure {newindex:02.0f}',
            'name': f'{name_prefix}{newindex:02.0f}',
            'type': 'itemselect',
            'removable': True,
            'value': dict(all_items=CHANNELS, selected=[CHANNELS[0]])
        }

        self.addChild(child)

registerParameterType('cryostatchannel', ChannelGroup, override=True)


class DAQ_0DViewer_Cryostat(DAQ_Viewer_base):
    """ Cryostat plugin class for a 0D viewer

    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It retrieves the data from a Cryostat using communication from an IMacRT.

    """
    params = comon_parameters+[
            {'title': 'IP address', 'name': 'ip', 'type': 'str'},
            {'title': 'Port', 'name': 'port', 'type': 'int', 'default': 23},
            {"title": "Channel", "name": "channel", "type": "cryostatchannel"}
    ]

    def ini_attributes(self) -> None:
        self.controller: Cryostat = None

    def commit_settings(self, param: Parameter) -> None:
         """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
         if param.name() in utils.iter_children(
             self.settings.child('channel'), []):
            data = []
            for child in self.settings.child('channel').children():
                labels = child.value()['selected']
                data.append(
                    DataFromPlugins(
                        name=child.name(),
                        data=[np.array([0]) for _ in labels],
                        labels=labels,
                        dim='Data0D'
                    )
                )
            self.dte_signal_temp.emit(
                DataToExport(
                    name="cryostat",
                    data=data
                )
            )
             

    def ini_detector(self, controller: Cryostat=None) -> tuple[str, bool]:
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_detector_init(slave_controller=controller)

        if self.is_master:
            self.controller = Cryostat(self.settings['ip'], self.settings['port'])
        
        self.dte_signal_temp.emit(
            DataToExport(
                name='cryostat',
                data=[DataFromPlugins(
                    name='Mock1',
                    data=[np.array([0]), np.array([0])],
                    dim='Data0D',
                    labels=["x", "y"]
                )]
            )
        )

        res = self.controller.connect()

        if res:
            info = "Connection with MMR3 established."
            initialized = True
        else:
            info = "Unable to retrieve data from MMR3."
            initialized = False
            
        return info, initialized

    def close(self) -> None:
        """Terminate the communication protocol"""
        self.controller.disconnect()

    def grab_data(self, Naverage: int=1, **kwargs) -> None:
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        
        data = []
        for child in self.settings.child('channel').children():
            labels = child.value()['selected'][:]
            subdata = [np.array([getattr(self.controller, label)])
                       for label in labels]
            data.append(DataFromPlugins(
                name=child.name(),
                data=subdata,
                labels=labels,
                dim='Data0D'
            ))

        self.dte_signal.emit(DataToExport(
            name='cryostat',
            data=data
        ))

    def stop(self) -> None:
        pass


if __name__ == '__main__':
    main(__file__)
