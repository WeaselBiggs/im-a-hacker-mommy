# I'm a hacker, mommy!

A Hollywood hacking console for [Omarchy](https://omarchy.org). Filling bars,
hex dumps, IP addresses with octets that quietly go over 255, a katakana rain
you can trigger on demand, and a set of commands that look plausible right up
until they finish.

It reads the colours of whatever Omarchy theme is currently active, so it
matches your desktop. No dependencies beyond Python 3.

## Install

```
git clone https://github.com/WeaselBiggs/im-a-hacker-mommy.git ~/.local/share/im-a-hacker-mommy
~/.local/share/im-a-hacker-mommy/install.sh
```

That does three things:

- links the script to `~/.local/bin/do-a-hacking`
- adds **Do A Hacking** to the Omarchy menu (`~/.config/omarchy/extensions/omarchy-menu.jsonc`)
- binds **SUPER + SHIFT + H** in `~/.config/hypr/bindings.lua`

Want a different key? `HACKING_KEY="SUPER + ALT + H" ./install.sh`.
`./uninstall.sh` removes all three and leaves the clone alone.

## Use

```
do-a-hacking            full-speed drama
do-a-hacking --fast     same drama, a fifth of the waiting
do-a-hacking --theme ~/.config/omarchy/themes/cyberdelia/colors.toml
```

Type `help` once you're in. Ctrl-C is handled cinematically. After a few
commands someone will hack you back, and two people will need to type on the
keyboard at once.

## Commands, and how each one falls apart

| command | looks like | ends up |
|---|---|---|
| `scan` | host enumeration | half the hosts are in your house. one is the kettle. |
| `trace <ip>` | global route trace | lands on 127.0.0.1, this laptop, this chair |
| `crack <target>` | one-character-at-a-time brute force | password was also on a post-it |
| `decrypt <file>` | military-grade decryption | a shopping list, or a haggis recipe |
| `mainframe` | backdoor into the mainframe | it's a Raspberry Pi with a Sharpie sticker |
| `firewall` | perimeter bypass | ufw, zero rules, walked straight through |
| `satellite` | acquire a satellite | the ISS asks you to stop |
| `enhance` | enhance | same pixels, bigger. 100% confidence. |
| `gui` | Visual Basic interface to track the killer's IP | it's you |
| `override` | override | nothing was overridden. felt good though. |

`ls`, `cat`, `whoami`, `sudo` and `rm -rf /` have their own letdowns. Unknown
words flash ACCESS DENIED and then quietly suggest `help`.
