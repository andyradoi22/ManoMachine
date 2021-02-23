def hex_to_int(address):
    return int(address, 16)


class Pc(object):

  def __init__(self):
    self.ram = Mem(1024 * 4)
    self.ar = Register(12)
    self.pc = Register(12)
    self.dr = Register(16)
    self.ac = Register(16)
    self.ir = Register(16)
    self.tr = Register(16)
    self.inp = Register(8)
    self.out = Register(8)
    self.sc = Register(3)
    self.e = Register(1)
    self.s = Register(1)
    self.r = Register(1)
    self.ien = Register(1)
    self.fgi = Register(1)
    self.fgo = Register(1)  


  def cla(self):
    print("D7I'T3B11: AC <- 0, SC <- 0")
    self.ac.clear()

  def cle(self):
    print("D7I'T3B10: E <- 0, SC <- 0")
    self.e.clear()

  def cma(self):
    print("D7I'T3B9: AC <- AC', SC <- 0")
    self.ac.complement()

  def cme(self):
    print("D7I'T3B8: E <- E', SC <- 0")
    self.e.complement()

  def cir(self):
    print("D7I'T3B7: AC <- shr(AC), AC(15) <- E, E <- AC(0), SC <- 0")
    self.e.word = self.ac.shift_r(self.e.word)

  def cil(self):
    print("D7I'T3B6: AC <- shl(AC), AC(0) <- E, E <- AC(15), SC <- 0")
    self.e.word = self.ac.shift_l(self.e.word)

  def inc(self):
    print("D7I'T3B5: AC <- AC + 1, SC <- 0")
    self.ac.inc()

  def spa(self):
    print("D7I'T3B4: if (AC(15) = 0) then (PC <- PC + 1), SC <- 0")
    if not self.ac.word & 0x8000:
          self.pc.inc()

  def sna(self):
    print("D7I'T3B3: if (AC(15) = 1) then (PC <- PC + 1), SC <- 0")
    if self.ac.word & 0x8000:
          self.pc.inc()

  def sza(self):
    print("D7I'T3B2: if (AC = 0) then (PC <- PC + 1), SC <- 0")
    if self.ac.word == 0:
          self.pc.inc()

  def sze(self):
    print("D7I'T3B1: if (E = 0) then (PC <- PC + 1), SC <- 0")
    if self.e.word == 0:
          self.pc.inc()

  def hlt(self):
    print("D7I'T3B0: S <- 0, SC <- 0")
    self.s.word = 0

  def inp_io(self):
    print("D7IT3B11: AC(0-7) <- INP, FGI <- 0")
    self.ac.word = self.ac.word & 0xFF00
    self.ac.word = self.ac.word | self.inp.word
    self.fgi.clear()

  def out_io(self):
    print("D7IT3B10: OUT <- AC(0-7), FGO <- 0")
    self.out.word = self.ac.word & 0xFF
    self.fgo.clear()

  def ski_io(self):
    print("D7IT3B9: if (FGI = 1) then (PC <- PC + 1)")
    if self.fgi.word == 1:
        self.pc.inc()

  def sko_io(self):
    print("D7IT3B8: if (FG0 = 1) then (PC <- PC + 1)")
    if self.fgo.word == 1:
        self.pc.inc()

  def ion_io(self):
    print("D7IT3B7: IEN <- 1")
    self.ien.word = 1

  def iof_io(self):
    print("D7IT3B6: IEN <- 0")
    self.ien.clear()

  def read_mem(self, reg_source):
      reg_source.word = self.ram.read(self.ar.word)

  def write_mem(self, reg):
      self.ram.write(self.ar.word, reg.word)

  def execute(self, program_start):
      self.pc.word = program_start
      self.s.word = 1
      while self.s.word == 1:
          self.tic()

  def and_mri(self, t):
      if t == 4:
          print("D0T4: DR <- M[AR]")
          self.read_mem(self.dr)
          self.sc.inc()
      elif t == 5:
          print("D0T5: AC <- AC & DR, SC <- 0")
          self.ac.and_logic(self.dr)
          self.sc.clear()

  def add_mri(self, t):
      if t == 4:
          print("D1T4: DR <- M[AR]")
          self.read_mem(self.dr)
          self.sc.inc()
      elif t == 5:
          print("D1T5: AC <- AC + DR, E <- out, SC <- 0")
          self.e.word = self.ac.logic_add(self.dr)
          self.sc.clear()

  def lda_mri(self, t):
      if t == 4:
          print("D2T4: DR <- M[AR]")
          self.read_mem(self.dr)
          self.sc.inc()
      elif t == 5:
          print("D2T5: AC <- DR, SC <- 0")
          self.ac.word = self.dr.word
          self.sc.clear()

  def sta_mri(self):
      print("D3T4: M[AR] <- AC, SC <- 0")
      self.write_mem(self.ac)
      self.sc.clear()

  def bun_mri(self):
      print("D4T4: PC <- AR, SC <- 0")
      self.pc.word = self.ar.word
      self.sc.clear()

  def bsa_mri(self, t):
      if t == 4:
          print("D5T4: M[AR] <- PC, AR <- AR + 1")
          self.write_mem(self.pc)
          self.ar.inc()
      elif t == 5:
          print("D5T5: PC <- AR, SC <- 0")
          self.pc.word = self.ar.word
          self.sc.clear()

  def isz_mri(self, t):
      if t == 4:
          print("D6T4: DR <- M[AR]")
          self.read_mem(self.dr)
          self.sc.inc()
      elif t == 5:
          print("D6T5: DR <- DR + 1")
          self.dr.inc()
          self.sc.inc()
      elif t == 6:
          print("D6T6: M[AR] <- DR, if(DR = 0) then PC <- PC + 1, SC <- 0")
          self.write_mem(self.dr)
          if self.dr.word == 0:
              self.pc.inc()
          self.sc.clear()

  def tic(self):
      t = self.sc.word
      r = self.r.word
      d = self.operation_cod()
      i = self.bit_indirect()
      if t < 3 and r == 1:
          self.stop(t)
      if t < 2 and r == 0:
          self.fetch(t)
      if t == 2 and r == 0:
          self.decode()
      if t == 3 and d != 7:
          self.op_fetch(i)
      if t > 3 and d != 7:
          self.memory_instruction(d, t)
      if t == 3 and d == 7:
          b = self.instruction_bit()
          if i == 0:
              self.io_instruction(b)
          else:
              self.register_instruction(b)

  def operation_cod(self):
      """
      Bits-> 12, 13, 14
      """
      return (self.ir.word >> 12) & 111

  def bit_indirect(self):
      """
      Bit->15
      0-> direct address
      1->indirect address
      """
      return (self.ir.word >> 15) & 1

  def stop(self, t):
      if t == 0:
          print("RT0: AR <- 0, TR <- PC")
          self.ar.clear()
          self.tr.word = self.pc.word
          self.sc.inc()
      elif t == 1:
          print("RT1: M[AR] <- TR, PC <- 0")
          self.write_mem(self.tr)
          self.pc.clear()
          self.sc.inc()
      elif t == 2:
          print("RT2: PC <- PC + 1, IEN <- 0, R <- 0, SC <- 0")
          self.pc.inc()
          self.ien.clear()
          self.r.clear()
          self.sc.clear()

  def fetch(self, t):
      if t == 0:
          print("R'T0: AR <- PC")
          self.ar.word = self.pc.word
          self.sc.inc()
      elif t == 1:
          print("R'T1: IR <- M[AR], PC <- PC + 1")
          self.read_mem(self.ir)
          self.pc.inc()
          self.sc.inc()

  def decode(self):
      print("R'T2: AR <- IR(0-11)")
      self.ar.word = self.ir.word
      self.sc.inc()

  def op_fetch(self, i):
      if i:
          print("D7'IT3: AR <- M[AR]")
          self.read_mem(self.ar)
      else:
          print("D7'I'T3: NOTHING")
      self.sc.inc()

  def instruction_bit(self):

    """
      Bits -> 0-11 -> Op
    """
    value = hex_to_int(self.ir.word)
    return value

  def memory_instruction(self, d, t):
      if d == 0:
          self.and_mri(t)
      elif d == 1:
          self.add_mri(t)
      elif d == 2:
          self.lda_mri(t)
      elif d == 3:
          self.sta_mri()
      elif d == 4:
          self.bun_mri()
      elif d == 5:
          self.bsa_mri(t)
      elif d == 6:
          self.isz_mri(t)

  def io_instruction(self, b):
      if b == 11:
          self.inp_io()
      elif b == 10:
          self.out_io()
      elif b == 9:
          self.ski_io()
      elif b == 8:
          self.sko_io()
      elif b == 7:
          self.ion_io()
      elif b == 6:
          self.iof_io()

  def register_instruction(self, b):
      if b == 11:
          self.cla()
      elif b == 10:
          self.cle()
      elif b == 9:
          self.cma()
      elif b == 8:
          self.cme()
      elif b == 7:
          self.cir()
      elif b == 6:
          self.cil()
      elif b == 5:
          self.inc()
      elif b == 4:
          self.spa()
      elif b == 3:
          self.sna()
      elif b == 2:
          self.sza()
      elif b == 1:
          self.sze()
      elif b == 0:
          self.hlt()


class Register(object):

    def __init__(self, number_of_bits):
        self.number_of_bits = number_of_bits
        self.word = 0
        self.aux = 1 << self.number_of_bits
        self.complement_aux = self.aux - 1

    def inc(self):
        self.word = self.word + 1

    def clear(self):
        self.word = 0

    def and_logic(self, new_word):
        self.word = self.word & new_word

    def complement(self):
        self.word = ~self.word & self.complement_aux

    def logic_add(self, new_word):
        val = self.word + new_word
        carry = val & self.aux
        self.word = val % self.aux
        if carry:
            return 1
        else:
            return 0

    def shift_r(self, msb):
        """
        msb-most significant bit
        lsb-last significant bit
        """
        lsb = self.word & 1
        self.word = self.word >> 1
        if msb:
            msb_nou = self.aux >> 1
            self.word = self.word | msb_nou
        return lsb

    def shift_l(self, lsb):
        msb_nou = self.aux >> 1
        if msb_nou & self.word:
            msb = 1
        else:
            msb = 0
        self.word = (self.word << 1) & self.complement_aux
        if lsb:
            self.word = self.word | 1
        return msb

    def __str__(self):
        return 'Register(word= %s)' % bin(self.word)[2:].zfill(self.number_of_bits)


class Mem(object):
    def __init__(self, length):
        self.length = length
        self.data = [0] * length

    def write(self, address, word):
        self.data[address] = word

    def read(self, address):
        return self.data[address]

    def __str__(self):
        return 'Memory(size=%dK)' % (self.length / 1024)






