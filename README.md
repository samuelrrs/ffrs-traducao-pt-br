# Tradução PT-BR — FINAL FANTASY RESONANCE (PS5 dump PPSA31544)

Patch de texto para o `en/Game.locres` do `ffrs-ps5.pak`. O menu em inglês passa a mostrar português.

**Não inclui o jogo.** Só o locres e o script de injeção.

Tradução: thesamzito (YouTube) e Juli Nos (YouTube).

## Requisitos

- Python 3 no PATH
- Dump `PPSA31544-app0` (o mesmo da PS5, com `ffrs\content\paks\ffrs-ps5.pak` e `ampr_emu.index`)

Não funciona colando `~mods` de PC na pasta de paks. Neste dump o texto tem de ir **dentro** do `ffrs-ps5.pak`.

## Uso

1. Mantenha os três arquivos juntos: `en-Game.locres.bin`, `aplicar_traducao.py`, `aplicar_traducao.bat`
2. Dê dois cliques em `aplicar_traducao.bat` e cole o caminho da pasta `PPSA31544-app0`
3. Ou no cmd:

```bat
aplicar_traducao.bat "D:\caminho\PPSA31544-app0"
```

O script faz backup `ffrs-ps5.pak.before-pt.bak`, troca o locres e atualiza o `ampr_emu.index`. Se já estiver aplicado, mostra `ja aplicado, nada a fazer`.
