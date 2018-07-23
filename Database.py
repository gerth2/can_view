##################################################################################################
# Users are allowed to define a Database to interpet CAN messages. This is designed to be
# flexible, with all interpretations defined in an xml file. This file will 
# consist of many known message formats, as well as information as to how to intepret pieces
# of data from them. For each received CAN message, the list of known messages will be scanned
# to see if any of them match. The first one will be used, and the database file is used to 
# interpret and display the data.
#
#  Stage 1: Matching the Message
#  -- User provides a "ID Mask" and "ID Compare" value
#   -- The CAN message's ID is first logical AND'ed with the mask, then compared to the Compare value
#   -- The CAN Message's data length is compared to an expected length
#   -- If the result of all of the above are TRUE, the message is interpreted using this interpreter
#
# Stage 2: Data Interpretation
#  -- For as many elements as desired, user provides the following: Name, Source, Mask, Downshift, Scale, Offset
#  -- The Source specified if the CAN ID or the CAN Data contain the data to be extracted
#  -- To calculate the value for a given data element, the following algorithm is used:
#   -- The selected bits are logically AND'ed with the Mask. 
#   -- This result is downshifted by "Downshift" bits
#   -- This result is converted to a double floating point value
#   -- This result is multiplied by the value Scale
#   -- This result is added with the value Offset
#   -- This result is displayed in the GUI, after the string Name
#
# Example XML:
#  <CanDatabase>
#    <Interpreter id_mask="0xFFFFFF00" id_compare="0x12345600" data_len=8>
#       <DataElem Name="Addr" Source="id" Mask="0x000000FF" Downshift=0 Scale=1 Offset=0/>
#       <DataElem Name="Speed" Source="data" Mask="0x00000000000AFF00" Downshift=8 Scale=0.125 Offset=0/>
#    </Interpreter>
#    <Interpreter>
#      ...
#    </Interpreter>
#  </CanDatabase>
#
#
#
##################################################################################################
import xml.etree.ElementTree as ET



class dbProcessor():

    msgInterpreterList = []

    def loadDb(self, fpath):
        with open(fpath, 'r') as f:
            #Reset interpreter list
            self.msgInterpreterList = []

            #Parse XML
            tree = ET.parse(fpath)
            xml_root = tree.getroot()

            if(xml_root != None):
                #For each message interpreter in the XML file, make a new interpreter
                for child in xml_root.findall('Interpreter'):
                    new_interpreter = msgInterpreter(child.get('id_mask'), 
                                                    child.get('id_compare'), 
                                                    int(child.get('data_len'),0))

                    #For each data interpreter in the message interpreter, add it.
                    for dataint in child:
                        new_interpreter.addDataInterpreter(dataint.get('Name'),
                                                        dataint.get('Source'),
                                                        int(dataint.get('Mask'),0),
                                                        int(dataint.get('Downshift'),0),
                                                        float(dataint.get('Scale')),
                                                        float(dataint.get('Offset')))
                    self.msgInterpreterList.append(new_interpreter)
        return

    def getInfo(self, can_id, can_data):
        #Uses the loaded database to interpret a CAN Message (ID + Data) 
        # into a python dictonary with the format:
        # { 
        #    'name': <name of message>,
        #    'data': {
        #               <element name>: <element val>
        #               <element name>: <element val>
        #               <element name>: <element val>
        #                ...
        #            }
        #            
        # }
        # 
        # If no matching interpretation of the message is found, returns None
        #
        retval = None

        for msgInt in self.msgInterpreterList:
            if(msgInt.checkID(can_id, can_data)):
                retval = {'name':msgInt.name,'data':{}}
                for dataint in msgInt.dataInterpreters:
                    retval['data'].append(dataint.intepret(can_id, can_data))

        return retval


class msgInterpreter():
    def __init__(self, id_mask, id_compare, exp_data_len):
        self.id_mask = id_mask
        self.id_compare = id_compare
        self.exp_data_len = exp_data_len
        self.dataInterpreters = []

    def addDataInterpreter(self, name, source, mask, downshift, scale, offset):
        newInterpreter = dataInterpreter(name, source, mask, downshift, scale, offset)
        self.dataInterpreters.append(newInterpreter)

    def checkID(self, can_id):
        working_val = can_id
        working_val &= self.id_mask
        if(working_val == self.id_compare):
            return True
        else:
            return False



class dataInterpreter():
    def __init__(self, name, source, mask, downshift, scale, offset):
        self.name = name
        self.source = source
        self.mask = mask
        self.downshift = downshift
        self.scale = scale
        self.offset = offset

    def interpret(self, can_id, can_data):
        if(self.source.contain("id")):
            working_val = can_id
        else:
            working_val = can_data

        working_val &= self.mask
        working_val = working_val >> self.downshift
        working_val *= self.scale
        working_val += self.offset

        retval = {self.name: str(working_val)}

        return retval
