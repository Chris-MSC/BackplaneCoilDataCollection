import serial

# Communication Connection
def comms(port, baud, timeout):
    try:
        ser=serial.Serial(port, baud, timeout=timeout)
        print("Connected")
        return(ser)

    except:
        print("Connection Error")
        return(1)


class ccTalk_read():
    def __init__(self, msg):
        self.msg = msg
        self.decimal = self.hex_convert()       
        self.message = self.msg_check()

    def msg_check(self):
        self.address = self.decimal[0]
        self.header = self.decimal[3]

        if self.decimal[1] == 0:
            self.length = 0
            self.data = None
        else:
            self.length = self.decimal[1]
            self.data = self.decimal[4:4 + self.decimal[1]]

        self.message = ccTalk_msg(self.address, self.length, self.header, self.data).message()
        
        if self.message == self.decimal:
            return(self.message)
        else:
            print('CRC check failed')
            return

    def hex_convert(self):
        bite_array = list(self.msg.hex())
    
        hex_array = []
        array_count = 0
        loop_count = int(len(bite_array)/2)
    
        for bit in range(loop_count):
            hex_array.append(bite_array[array_count] + bite_array[array_count+1])
            array_count += 2
    
        dec_array = []
        array_count = 0
        loop_count = int(len(hex_array))

        for bit in range(loop_count):
            dec_array.append(int(hex_array[array_count], 16))
            array_count += 1

        return(dec_array)

    def slave_msg_label(self):
        header_types = {
        '[1, 0, 48, 0, 55]' : "ACK"
        }
        string_convert = str(self.message)
        
        if string_convert != "1":
            return(header_types.get(string_convert))
        else:
            return(": CRC check failed")


class ccTalk_msg():
    def __init__(self, address, length, header, data):
        self.address = address
        self.length = length
        self.header = header
        
        if data != None:
            if self.length > 1:
                self.data = []
                for bite in data:
                    self.data.append(bite)
        
            else:
                self.data = data
        
        else:
            self.data = data
        
        
            
    def message(self):
        result = []
        result.append(self.address)
        result.append(self.length)
        
        crc_hex = self.crc_calculation()
        self.crc_lsb = int(crc_hex[1], 16)
        self.crc_msb = int(crc_hex[0], 16)
        
        result.append(self.crc_lsb)
        result.append(self.header)

        if self.data != None:
            if self.length > 1:
                for bite in self.data:
                    result.append(bite)
        
            elif self.length == 1:
                result.append(self.data[0])

        result.append(self.crc_msb)
            
        return result

    def crc_calculation(self):
        """
        Calculates the CCITT checksum (CRC16) that can be used as a ccTalk
        checksuming algorithm
        """
        if self.data == None:
            array = [self.address, self.length, self.header]
        else:
            array = [self.address, self.length, self.header] + self.data


        crc = 0x0000    # Initial CRC register
        poly = 0x1021   # CRC polynomial

        ##############*CRC Algorithm*########################
        for bite in array:                                  #
            crc ^= (bite << 8) & 0xffff                     #
            for j in range(0, 8):                           #
                if crc & 0x8000:                            #
                    crc = ((crc << 1) ^ poly) & 0xffff      #
                else:                                       #
                    crc <<= 1                               #
                    crc &= 0xffff                           # 
        ##################################################### Result is in Decimal request Hex conversion        
        
        hex = '{0:x}'.format(crc)       
        hex_convert = list(hex)
        crc_array = [hex_convert[0] + hex_convert[1], hex_convert[2] + hex_convert[3]] # [LSB, MSB] string clean up
        
        return(crc_array)                                          

    def host_msg_label(self):
        header_types = {
        255 : 'Factory set:up and test',
        254 : 'Simple poll',
        253 : 'Address poll',
        252 : 'Address clash',
        251 : 'Address change',
        250 : 'Address random',
        249 : 'Request polling priority',
        248 : 'Request status',
        247 : 'Request variable set',
        246 : 'Request manufacturer id',
        245 : 'Request equipment category id',
        244 : 'Request product code',
        243 : 'Request database version',
        242 : 'Request serial number',
        241 : 'Request software revision',
        240 : 'Test solenoids',
        239 : 'Operate motors',
        238 : 'Test output lines',
        237 : 'Read input lines',
        236 : 'Read opto states',
        235 : 'Read last credit or error code',
        234 : 'Issue guard code',
        233 : 'Latch output lines',
        232 : 'Perform self:check',
        231 : 'Modify inhibit status',
        230 : 'Request inhibit status',
        229 : 'Read buffered credit or error codes',
        228 : 'Modify master inhibit status',
        227 : 'Request master inhibit status',
        226 : 'Request insertion counter',
        225 : 'Request accept counter',
        224 : 'Dispense coins',
        223 : 'Dispense change',
        222 : 'Modify sorter override status',
        221 : 'Request sorter override status',
        220 : 'One:shot credit',
        219 : 'Enter new PIN number',
        218 : 'Enter PIN number',
        217 : 'Request payout high / low status',
        216 : 'Request data storage availability',
        215 : 'Read data block',
        214 : 'Write data block',
        213 : 'Request option flags',
        212 : 'Request coin position',
        211 : 'Power management control',
        210 : 'Modify sorter paths',
        209 : 'Request sorter paths',
        208 : 'Modify payout absolute count',
        207 : 'Request payout absolute count',
        206 : 'Empty payout',
        205 : 'Request audit information block',
        204 : 'Meter control',
        203 : 'Display control',
        202 : 'Teach mode control',
        201 : 'Request teach status',
        200 : 'Upload coin data',
        199 : 'Configuration to EEPROM',
        198 : 'Counters to EEPROM',
        197 : 'Calculate ROM checksum',
        196 : 'Request creation date',
        195 : 'Request last modification date',
        194 : 'Request reject counter',
        193 : 'Request fraud counter',
        192 : 'Request build code',
        191 : 'Keypad control',
        190 : 'Request payout status',
        189 : 'Modify default sorter path',
        188 : 'Request default sorter path',
        187 : 'Modify payout capacity',
        186 : 'Request payout capacity',
        185 : 'Modify coin id',
        184 : 'Request coin id',
        183 : 'Upload window data',
        182 : 'Download calibration info',
        181 : 'Modify security setting',
        180 : 'Request security setting',
        179 : 'Modify bank select',
        178 : 'Request bank select',
        177 : 'Handheld function',
        176 : 'Request alarm counter',
        175 : 'Modify payout float',
        174 : 'Request payout float',
        173 : 'Request thermistor reading',
        172 : 'Emergency stop',
        171 : 'Request hopper coin',
        170 : 'Request base year',
        169 : 'Request address mode',
        168 : 'Request hopper dispense count',
        167 : 'Dispense hopper coins',
        166 : 'Request hopper status',
        165 : 'Modify variable set',
        164 : 'Enable hopper',
        163 : 'Test hopper',
        162 : 'Modify inhibit and override registers',
        161 : 'Pump RNG',
        160 : 'Request cipher key',
        159 : 'Read buffered bill events',
        158 : 'Modify bill id',
        157 : 'Request bill id',
        156 : 'Request country scaling factor',
        155 : 'Request bill position',
        154 : 'Route bill',
        153 : 'Modify bill operating mode',
        152 : 'Request bill operating mode',
        151 : 'Test lamps',
        150 : 'Request individual accept counter',
        149 : 'Request individual error counter',
        148 : 'Read opto voltages',
        147 : 'Perform stacker cycle',
        146 : 'Operate bi:directional motors',
        145 : 'Request currency revision',
        144 : 'Upload bill tables',
        143 : 'Begin bill table upgrade',
        142 : 'Finish bill table upgrade',
        141 : 'Request firmware upgrade capability',
        140 : 'Upload firmware',
        139 : 'Begin firmware upgrade',
        138 : 'Finish firmware upgrade',
        137 : 'Switch encryption code',
        136 : 'Store encryption code',
        135 : 'Set accept limit',
        134 : 'Dispense hopper value',
        133 : 'Request hopper polling value',
        132 : 'Emergency stop value',
        131 : 'Request hopper coin value',
        130 : 'Request indexed hopper dispense count',
        129 : 'Read barcode data',
        128 : 'Request money in',
        127 : 'Request money out',
        126 : 'Clear money counters',
        125 : 'Pay money out',
        124 : 'Verify money out',
        123 : 'Request activity register',
        122 : 'Request error status',
        121 : 'Purge hopper',
        120 : 'Modify hopper balance',
        119 : 'Request hopper balance',
        118 : 'Modify cashbox value',
        117 : 'Request cashbox value',
        116 : 'Modify real time clock',
        115 : 'Request real time clock',
        114 : 'Request USB id',
        113 : 'Switch baud rate',
        112 : 'Read encrypted events',
        111 : 'Request encryption support',
        110 : 'Switch encryption key',
        109 : 'Request encrypted hopper status',
        108 : 'Request encrypted monetary id',
        107 : "Operate escrow",
        106 : 'Request escrow status',
        105 : 'Data stream',
        104 : 'Request service status',
        4 : 'Request comms revision',
        3 : 'Clear comms status variables',
        2 : 'Request comms status variables',
        1 : 'Reset device',
        0 : 'Reply'
        }
        return(header_types.get(self.header))


class ccTalk_write():
    def __init__(self, cmd):
        self.cmd = cmd

    def command(self):
        self.parameters = self.cmd_msg_label()
        
        if len(self.parameters) < 4:
            self.address = self.parameters[0]
            self.length = self.parameters[1]
            self.header = self.parameters[2]
            self.data = None
        else:
            self.address = self.parameters[0]
            self.length = self.parameters[1]
            self.header = self.parameters[2]
            self.data = self.parameters[3:]
            
        host_msg = ccTalk_msg(self.address, self.length, self.header, self.data).message()
        host_label = ccTalk_msg(self.address, self.length, self.header, self.data).host_msg_label()
        val364.write(host_msg)
        print("Sent message ", host_msg, host_label)

        slave_msg_head = val364.read(4)
        try:
            slave_msg_tail = val364.read(slave_msg_head[1] + 1)
            slave_msg_raw = slave_msg_head + slave_msg_tail
            slave_msg = ccTalk_read(slave_msg_raw).msg_check()
            slave_label = ccTalk_read(slave_msg_raw).slave_msg_label()
            print("Recieved message", slave_msg, slave_label)
        except:
            print(slave_msg_head, 'No response or an error occured')
               
    def cmd_msg_label(self):
        command_types = {
            'poll' : [55, 0, 254],
            'enable' : [55, 1, 231, 255],
            'request id' : [55, 0, 245],
            'gate' : [55, 1, 240, 1],
            'sorter 1' : [55, 2, 240, 0, 1]
        }
        return(command_types.get(self.cmd))


if __name__ == "__main__":
    # Serial Communication Parameters
    com_port = "COM3"
    baud_rate = 57600
    timeout = 2
    
    # Main code
    val364 = comms(com_port, baud_rate, timeout)
    
    ccTalk_write('poll').command()
    ccTalk_write('enable').command()
    ccTalk_write('request id').command()
    ccTalk_write('gate').command()