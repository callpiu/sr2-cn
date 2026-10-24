import sys,struct,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_EDI
import pefile
from build_fix import build,sha,ORIGINAL_SHA256
ROOT=Path('G:/SteamLibrary/steamapps/common/Saints Row 2');out=Path(__file__).parent/'analysis'
original=(ROOT/'SR2_pc.exe').read_bytes()
if sha(original)!=ORIGINAL_SHA256:
    original=(ROOT/'SR2_pc.exe.before_heli_fix_20261023.bak').read_bytes()
patched=build(original)
pe=pefile.PE(data=original)
CASES={0xff6299d9:0xe25f84,0x2370e5a4:0xe25f40,0xaf10621e:0xe25ed0,0xf284ed87:0xe25e78,0xab55ce3b:0xe25e30,0x42363fc7:0xe25dec,0xa200759a:None,0x510409b8:None,0x12345678:None}
TARGETS={0xaf10621e,0xf284ed87};FALLBACK=0x18000000
def run(data,lang,hx):
    u=Uc(UC_ARCH_X86,UC_MODE_32)
    for base,size in [(0x7f4000,0x2000),(0xbdc000,0x1000),(0xe8c000,0x1000),(0x10000000,0x10000),(FALLBACK,0x1000)]:u.mem_map(base,size)
    u.mem_write(0x7f4000,data[0x3f4000:0x3f6000]);u.mem_write(0xbdc9b0,b'\xc3')
    u.mem_write(0xe8c470,struct.pack('<I',lang));u.mem_write(0x10008000,struct.pack('<I',0x10001000))
    u.reg_write(UC_X86_REG_ESP,0x10008000);u.reg_write(UC_X86_REG_ECX,0x10000100)
    u.reg_write(UC_X86_REG_ESI,0x76543210);u.reg_write(UC_X86_REG_EDI,0x23456789)
    calls=[]
    def hook(uc,address,size,unused):
        if address==0xbdc9b0:uc.reg_write(UC_X86_REG_EAX,hx)
        elif address==0x7f4d60:
            sp=uc.reg_read(UC_X86_REG_ESP)
            calls.append(struct.unpack('<I',bytes(uc.mem_read(sp+4,4)))[0])
            ret=struct.unpack('<I',bytes(uc.mem_read(sp,4)))[0]
            uc.reg_write(UC_X86_REG_EAX,FALLBACK);uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x7f4bc0,0x10001000,count=150)
    assert u.reg_read(UC_X86_REG_EIP)==0x10001000
    assert u.reg_read(UC_X86_REG_ESP)==0x10008004
    assert u.reg_read(UC_X86_REG_ESI)==0x76543210 and u.reg_read(UC_X86_REG_EDI)==0x23456789
    return u.reg_read(UC_X86_REG_EAX),calls
tested=[]
for lang in range(14):
    for hx in CASES:
        before=run(original,lang,hx);after=run(patched,lang,hx)
        if lang==13 and hx in TARGETS:
            assert before==(CASES[hx],[]) and after==(FALLBACK,[hx])
        else:assert before==after,(lang,hex(hx),before,after)
        tested.append({'language':lang,'hash':hex(hx),'before_pointer':hex(before[0]),'after_pointer':hex(after[0]),'calls_before':before[1],'calls_after':after[1]})
for bad in (original[:-1],patched,original[:0x300]+b'X'+original[0x301:]):
    try:build(bad)
    except ValueError:pass
    else:raise AssertionError('Unsupported input was accepted')
report=dict(passed=True,emulated_cases=len(tested),stack_and_callee_saved_registers_preserved=True,unsupported_inputs_rejected=3,original_sha256=sha(original),patched_sha256=sha(patched),cases=tested)
(out/'emulation-tests.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
