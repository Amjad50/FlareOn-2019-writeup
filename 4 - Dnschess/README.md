Dnschess <!-- omit in toc -->
---

```
Some suspicious network traffic led us to this unauthorized chess program running on an Ubuntu desktop. This appears to be the work of cyberspace computer hackers. You'll need to make the right moves to solve this one. Good luck!
```

```
$ file capture.pcap ChessUI ChessAI.so 
capture.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Ethernet, capture length 262144)

ChessUI:      ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=c30ec8b70e255aec7c93eb80321e4eab7bd52b3f, for GNU/Linux 3.2.0, stripped

ChessAI.so:   ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=ed3bd3fae8d4a8e27e4565f31c9af58231319190, stripped
```

- [Introduction](#introduction)
- [Information Collection](#information-collection)
  - [ChessUI](#chessui)
  - [ChessAI.so](#chessaiso)
- [Solution](#solution)

## Introduction

This time its a Linux executable along with a dynamic library
(.so) as stated in `file` output.

Also there is a (.pcap) file which is a capture of network traffic.

This challenge's name is `DNS`chess, so it has something to do with
`DNS` (Domain Name System). This `pcap` might have `DNS` captures.


## Information Collection

Lets check the `pcap` file first:

![pcap first view](screenshots/pcap_first_view.png)

All the `pcap` is just `DNS` requests and responds. The app sends a requests
to a subdomain of `game-of-thrones.flare-on.com`. And this subdomain
appears to be kind of a chess piece move.

Example:
- move `rock`   from `c3` to `c6`.
- move `knight` from `g1` to `f3`.

That's a really weird way to send a chess move into a server.

### ChessUI
In this challenge there is a `main` function, so lets check it.

``` C
// this code is generated using Ghidra's decompilation.
int main(int uParm1,char *uParm2)
{
    /*
    ... trunked
    */
    // FUN_00103ab0 seems interesting because its the only
    // function refernce.
    g_signal_connect_data(uVar2,"activate",FUN_00103ab0,0,0,0);
    /*
    ... trunked
    */
}
```
From the main function, and after some research. it turned out that this is a `gnome application`.

This is an example of `Hello World` of `gnome` application:

``` C
#include <gtk/gtk.h>

// this is being referenced the same way as `FUN_00103ab0`
static void
activate (GtkApplication *app, pointer user_data)
{
    GtkWidget *window;
    GtkWidget *label;

    window = gtk_application_window_new (app);
    label = gtk_label_new ("Hello GNOME!");
    gtk_container_add (GTK_CONTAINER (window), label);
    gtk_window_set_title (GTK_WINDOW (window), "Welcome to GNOME");
    gtk_window_set_default_size (GTK_WINDOW (window), 200, 100);
    gtk_widget_show_all (window);
}

int
main (int argc, char **argv)
{
    GtkApplication *app;
    int status;

    app = gtk_application_new (NULL, G_APPLICATION_FLAGS_NONE);
    g_signal_connect (app, "activate", G_CALLBACK (activate), NULL);    // same as above
    status = g_application_run (G_APPLICATION (app), argc, argv);
    g_object_unref (app);

    return status;
}
```
next is `FUN_00103ab0`:
``` C
void FUN_00103ab0(undefined8 uParm1)
{
    /*
    ... trunked
    */
    undefined8 error_holder;
    long chessAILib;
    undefined *getAIName_func;
    undefined *getAIGreeting_func;
    /*
    ... trunked
    */

    // opens the `ChessAI` shared library file
    chessAILib = dlopen("./ChessAI.so",1);
    if (chessAILib != 0) {

        // gets `getAiName` function reference.
        getAIName_func = (undefined *)dlsym(chessAILib, "getAiName");
        /*
        ... trunked
        */

        // gets `getAiGreeting` function reference.
        getAIGreeting_func = (undefined *)dlsym(chessAILib, "getAiGreeting");
        /*
        ... trunked
        */

        // gets `getNextMove` function reference.
        `_global_getNextMove_func` = dlsym(chessAILib, "getNextMove");
        /*
        ... trunked
        */

        // call getAIName and getAIGreeting and store results
        // in global variables
        DAT_0010d078 = (*(code *)getAIName_func)();
        DAT_0010d070 = (*(code *)getAIGreeting_func)();
        /*
            ... trunked, cleaning up
        */

        // this seems to start the game loop and logic
        FUN_00103a40(0,0);
        return;
    }
    /*
    ... trunked
    */
}
```
The code above:
- It opens `ChessAi.so` library and gets three functions:
    - `getAIName`
    - `getAIGreeting`
    - `getNextMove`
- `getAIName` and `getAIGreeting` are called once and the result is stored in global variables. After that the function is not being called again.
- `getNextMove` is not being called in this function but instead is being stored in a global variable. So its mostly called from other places.
- `FUN_00103a40` which seems an interesting function because
its the only way to go next is being called.

Because `FUN_00103a40` seems like a logic/loop handler we 
are going for `_global_getNextMove_func`.

We get two XREF of `_global_getNextMove_func`:
- A `mov` instruction, which is the instruction that stores the reference to it.
- A `call` instruction from `FUN_00104310` which is more interesting.

``` C
int FUN_00104310(uint *arg1)
{
    iVar2 = (*_global_getNextMove_func)
                ((ulong)DAT_0010d120,   // global counter
                arg1 + 2,               // pointer after arg[0] and arg[1]
                (ulong)*arg1,           // arg1[0]
                (ulong)arg1[1],         // arg[1]
                &local_138);            // place holder for buffer

    /*
    ... trunked
    */
    DAT_0010d120 = DAT_0010d120 + 1; // global counter, increment
}
```
### ChessAI.so
 `ChessAI.so` has 3 exported functions:
``` C
char *getAiGreeting(void)
{
    return "Finally, a worthy opponent. Let us begin";
}

char *getAiGreeting(void)
{
  return "Finally, a worthy opponent. Let us begin";
}

// removed unimportant code from below
ulong getNextMove(uint arg1,char *arg2,uint arg3,uint arg4,uint *arg5)
{
    hostent *hostNetStruct;
    char buffer [72];
    char *ipAddress;
    
    // arg2 is chess piece name
    strcpy(buffer,arg2);

    // FUN_00101145 decodes arg3 & arg4 to chess position string
    // and `strcat` it to buffer.
    FUN_00101145(buffer,(ulong)arg3,(ulong)arg3);
    FUN_00101145(buffer,(ulong)arg4,(ulong)arg4);

    // add the main domain for the DNSchess
    strcat(buffer,".game-of-thrones.flare-on.com");

    // resolve domain name
    hostNetStruct = gethostbyname(buffer);

    if ((hostNetStruct == NULL) ||
        // get the ip address and check if the first part is not equal to (127)
        (ipAddress = *hostNetStruct->h_addr_list, *ipAddress != 127) ||
        // check if the last part of ip is odd
        ((ipAddress[3] & 1U) != 0) ||
        // check if the lowest 4 bits of the third part of the ip is 
        // not equal to the `arg1` which is the global counter from
        // chessUI
        (arg1 != ((uint)(byte)ipAddress[2] & 0xf))) {
            /*
            .. trunked
            */
    } else {
        // DAT_00102020 is a binary data (check below)
        //
        // DAT_00104060 is '\0' * 30 + "@flare-on.com"
        //
        // so DAT_00104060 is the flag location
        // and DAT_00102020 is the flag encrypted by XORed
        // with the second value of the ip address at the location of arg1
        // two bytes are XORed at a time with one key
        (&DAT_00104060)[(ulong)(arg1 * 2)] = (&DAT_00102020)[(ulong)(arg1 * 2)] ^ ipAddress[1];
        (&DAT_00104060)[(ulong)(arg1 * 2 + 1)] = (&DAT_00102020)[(ulong)(arg1 * 2 + 1)] ^ ipAddress[1];

        /*
        ... trunked
        */
    }
}
```

the content of `DAT_00102020`, len == 30: 
```
79 5a b8 bc ec d3 df dd 99 a5 b6 ac 15 36 85 8d 09 08 77 52 4d 71 54 7d a7 a7 08 16 fd d7
```

In conclusion:
- there is some checks at the beginning of `getNextMove`, and if they all passed. Then two bytes are decrypted and stored into the flag string buffer.
    - hostNetStruct must be NOT NULL.
    - the first entry in the ip address is (127).
    - the last entry in the ip address is even.
    - the lowest 4 bits of the third entry in the ip address is equal to the counter passed as `arg1` to `getNextMove` 
- `DAT_00102020` is the encrypted flag, its decrypted by XOR with the second
value of the ip address which is being obtained from the DNS server if the checks passed.
- each decryption cycle decrypts two bytes.
- the pcap attached is mostly a recording of someone who won the game. All IP address are stored in it.

## Solution
The IP addresses from the `pcap` file is extracted in [address.txt](addresses.txt).

The solution is written in python [here](solution_script.py).

Highlights:
- read the addresses from the file
``` python
addresses_file = open('addresses.txt', 'r')
addresses = []

for line in addresses_file.readlines():
    line = line.split('.')
    addresses.append(
        list(map(int, line))
    )
```

- putting the encoded flag in the code manually and initialize a new empty array
for the result flag.

``` python
encoded_flag = [121, 90, 184, 188, ...]

decoded_flag = [0] * len(encoded_flag)
```
from the checks in `getNextMove` the first two are always true, and we need to focus on the last two.

- decrypt the flag

``` python
for address in addresses:
    # address[3] is even
    if(address[3] & 0x1 == 0):
        index = address[2] & 0xf
        
        # decrypt two bytes
        decoded_flag[index * 2] = encoded_flag[index * 2] ^ address[1]
        decoded_flag[index * 2 + 1] = encoded_flag[index * 2 + 1] ^ address[1]

print("flag:", ''.join(map(chr, decoded_flag)) + "@flare-on.com")
```

In here because we don't have `arg1` which is being used as the index to which bytes to decrypt. But we know that to pass the checks `arg1` must be equal to the lowest 4 bits in `address[2]` so we use it.

When running the script we get

```
flag: LooksLikeYouLockedUpTheLookupZ@flare-on.com
```
