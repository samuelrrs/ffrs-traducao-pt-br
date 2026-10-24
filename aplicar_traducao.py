# -*- coding: utf-8 -*-
"""Injeta en-Game.locres.bin no ffrs-ps5.pak de um PPSA31544-app0 e atualiza ampr_emu.index."""
import os, sys, struct, hashlib, shutil

ENTRY = 315487621
HEADER = 53
GUID = bytes.fromhex("0e147475674a03fc4a15909dc3377f1b")
FILES = 2366
BUMPED = 226
PAK_REL = os.path.join("ffrs", "content", "paks", "ffrs-ps5.pak")
AMPR_NAME = "ampr_emu.index"
HERE = os.path.dirname(os.path.abspath(__file__))
LOCRES_BIN = os.path.join(HERE, "en-Game.locres.bin")

def walk(enc):
    pos = 0
    rows = []
    while pos < len(enc):
        bitfield = struct.unpack_from("<I", enc, pos)[0]; pos += 4
        if (bitfield & 0x3F) == 0x3F:
            pos += 4
        method = (bitfield >> 23) & 0x3F
        off_at = pos
        if bitfield & (1 << 31):
            file_off = struct.unpack_from("<I", enc, pos)[0]; off_w = 4; pos += 4
        else:
            file_off = struct.unpack_from("<Q", enc, pos)[0]; off_w = 8; pos += 8
        size_at = pos
        if bitfield & (1 << 30):
            uncomp = struct.unpack_from("<I", enc, pos)[0]; size_w = 4; pos += 4
        else:
            uncomp = struct.unpack_from("<Q", enc, pos)[0]; size_w = 8; pos += 8
        if method != 0:
            pos += 4 if bitfield & (1 << 29) else 8
        if ((bitfield >> 6) & 0xFFFF) > 1:
            raise SystemExit("pak com blocos inesperados")
        rows.append((file_off, uncomp, off_at, off_w, size_at, size_w))
    return rows

def patch_ampr(ampr_path, pak_size_old, pak_size_new):
    blob = bytearray(open(ampr_path, "rb").read())
    needle = b"/app0/ffrs/content/paks/ffrs-ps5.pak"
    pos = blob.find(needle)
    if pos < 0:
        raise SystemExit("ampr_emu.index sem o path do ffrs-ps5.pak")
    # records: u32 path_off, u32 path_len, u64 size; strings at 1344+path_off
    base = 1344
    path_off = pos - base
    rec = None
    for off in range(0, min(len(blob), base) - 16):
        po, pl, sz = struct.unpack_from("<IIQ", blob, off)
        if po == path_off and pl == len(needle) and sz == pak_size_old:
            rec = off
            break
    if rec is None:
        raise SystemExit("registro AMPR do pak nao encontrado (dump diferente?)")
    struct.pack_into("<Q", blob, rec + 8, pak_size_new)
    open(ampr_path, "wb").write(blob)
    print("AMPR ok offset", rec)

def apply(app0, bak_name="ffrs-ps5.pak.before-pt.bak"):
    app0 = os.path.abspath(app0)
    src = os.path.join(app0, PAK_REL)
    ampr = os.path.join(app0, AMPR_NAME)
    if not os.path.isfile(src):
        raise SystemExit("nao achei " + src)
    if not os.path.isfile(ampr):
        raise SystemExit("nao achei " + ampr)
    if not os.path.isfile(LOCRES_BIN):
        raise SystemExit("nao achei " + LOCRES_BIN)
    payload = open(LOCRES_BIN, "rb").read()
    with open(src, "rb") as f:
        f.seek(ENTRY + 8)
        OLD = struct.unpack("<qq", f.read(16))[0]
    delta = len(payload) - OLD
    print("alvo", src)
    print("OLD", OLD, "new", len(payload), "delta", delta)
    if delta == 0:
        with open(src, "rb") as f:
            f.seek(ENTRY + HEADER)
            if f.read(len(payload)) == payload:
                print("ja aplicado, nada a fazer")
                return
        raise SystemExit("tamanho igual mas conteudo diferente — pare e confira o dump")
    for sample, must16 in (("Magilâmina", True), ("Santuário do Fogo", True), ("Português", True), ("Carregar", False)):
        u16 = sample.encode("utf-16le")
        u8 = sample.encode("utf-8")
        if must16 or any(ord(c) > 127 for c in sample):
            assert u16 in payload, sample
        else:
            assert (u8 in payload) or (u16 in payload), sample
    payload_off = ENTRY + HEADER
    payload_end = payload_off + OLD
    src_size = os.path.getsize(src)
    magic_at = src_size - 204
    with open(src, "rb") as f:
        f.seek(magic_at)
        magic, ver, ioff, isize = struct.unpack("<IiQQ", f.read(24))
        ih = f.read(20)
        f.seek(ioff)
        idx0 = f.read(isize)
    assert magic == 0x5A6F12E1 and ver == 11 and hashlib.sha1(idx0).digest() == ih
    dst = src + ".pt-apply"
    if os.path.exists(dst):
        os.remove(dst)
    buf = 8 * 1024 * 1024
    with open(src, "rb") as s, open(dst, "wb") as d:
        remain = payload_off
        while remain:
            chunk = s.read(min(buf, remain))
            if not chunk:
                raise SystemExit("leitura curta")
            d.write(chunk)
            remain -= len(chunk)
        d.write(payload)
        s.seek(payload_end)
        while True:
            chunk = s.read(buf)
            if not chunk:
                break
            d.write(chunk)
    assert os.path.getsize(dst) == src_size + delta
    with open(dst, "r+b") as f:
        f.seek(ENTRY + 8)
        f.write(struct.pack("<qq", len(payload), len(payload)))
        f.seek(ENTRY + 28)
        f.write(hashlib.sha1(payload).digest())
        idx_at = ioff + delta
        f.seek(idx_at)
        idx = bytearray(f.read(isize))
        p = 0
        n = struct.unpack_from("<i", idx, p)[0]; p += 4 + n
        files = struct.unpack_from("<i", idx, p)[0]; p += 4
        assert files == FILES, files
        p += 8 + 4
        ph_pos = p
        ph_off, ph_size = struct.unpack_from("<qq", idx, p); p += 16
        p += 20 + 4
        dir_pos = p
        dir_off, dir_size = struct.unpack_from("<qq", idx, p); p += 16
        p += 20
        enc_size = struct.unpack_from("<i", idx, p)[0]; p += 4
        enc_pos = p
        struct.pack_into("<q", idx, ph_pos, ph_off + delta)
        struct.pack_into("<q", idx, dir_pos, dir_off + delta)
        enc = bytearray(idx[enc_pos:enc_pos + enc_size])
        rows = walk(enc)
        assert len(rows) == FILES
        bumped = sized = 0
        for file_off, uncomp, off_at, off_w, size_at, size_w in rows:
            if ENTRY < file_off < payload_end:
                raise SystemExit("arquivo no meio do locres")
            if file_off >= payload_end:
                struct.pack_into("<I" if off_w == 4 else "<Q", enc, off_at, file_off + delta)
                bumped += 1
            if file_off == ENTRY and uncomp == OLD:
                struct.pack_into("<I" if size_w == 4 else "<Q", enc, size_at, len(payload))
                sized += 1
        assert sized == 1 and bumped == BUMPED, (sized, bumped)
        idx[enc_pos:enc_pos + enc_size] = enc
        f.seek(idx_at)
        f.write(idx)
        new_hash = hashlib.sha1(idx).digest()
        f.seek(magic_at + delta + 8)
        f.write(struct.pack("<Q", ioff + delta))
        f.seek(magic_at + delta + 24)
        f.write(new_hash)
        f.seek(payload_off)
        assert f.read(len(payload)) == payload
        f.seek(payload_off + len(payload) + HEADER)
        assert f.read(16) == GUID
        f.seek(ioff + delta)
        assert hashlib.sha1(f.read(isize)).digest() == new_hash
    print("VERIFY OK")
    bak = os.path.join(os.path.dirname(src), bak_name)
    if os.path.exists(bak):
        print("backup ja existe, mantido:", bak)
        os.remove(src)
    else:
        os.replace(src, bak)
        print("backup", bak)
    os.replace(dst, src)
    patch_ampr(ampr, src_size, src_size + delta)
    print("SWAPPED", os.path.getsize(src))

def resolve_app0(path):
    path = os.path.abspath(path.strip().strip('"'))
    cur = path
    for _ in range(6):
        if os.path.isfile(os.path.join(cur, PAK_REL)) and os.path.isfile(os.path.join(cur, AMPR_NAME)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise SystemExit("nao achei PPSA31544-app0 em: " + path)

def pause():
    if os.environ.get("FFRS_FROM_BAT"):
        return
    try:
        input("\nPressione Enter para sair...")
    except EOFError:
        pass

def pick_app0():
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        return sys.argv[1]
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askdirectory(title="Selecione a pasta PPSA31544-app0 do jogo")
        root.destroy()
        return path
    except Exception:
        print("Cole o caminho da pasta PPSA31544-app0 do jogo.")
        try:
            return input("Pasta app0: ").strip().strip('"')
        except EOFError:
            return ""

if __name__ == "__main__":
    code = 0
    try:
        path = pick_app0()
        if not path:
            print("Nenhuma pasta informada.")
            code = 1
        else:
            apply(resolve_app0(path))
    except SystemExit as e:
        if e.code not in (0, None):
            if isinstance(e.code, int):
                code = e.code
            else:
                print(e.code)
                code = 1
    except Exception as e:
        print("ERRO:", e)
        code = 1
    pause()
    sys.exit(code)
