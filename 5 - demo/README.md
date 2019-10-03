demo
---

```
Someone on the Flare team tried to impress us with their demoscene skills. It seems blank. See if you can figure it out or maybe we will have to fire them. No pressure.
```

```
$ file 4k.exe 
4k.exe: MS-DOS executable
```

- [Introduction](#introduction)
- [Information Collection](#information-collection)
- [Solution](#solution)

## Introduction
From the `file` command, this is a windows executable.

`demoscene` word was new to me, so I searched and found [this](https://en.wikipedia.org/wiki/Demoscene), so this might be some kind of drawing?

Just to skip the process, I tried to analyze this using `Ghidra`.
There was only **one** function: `entry`, which seems very weird to have only
one function, seemed a complex function and didn't try to analyze it.

So I used `dynamic analysis` to solve this challenge.
<br>
I'm using `x32dbg` (which is a debugger for windows) as my main dynamic analysis tool.

## Information Collection

First, lets run the program. This is the output:
![demo first screen](screenshots/demo_first_screen.png)

Its showing 3D drawing of `flare` and its rotating.
<br>
From the code of entry there was no 3D functions, nor Windows functions.
<br>
I'm guessing its going to be built by the program (self generating code).

Now to debugging:

In `x32dbg` when loading a binary, it sets an automatic `breakpoint` (point to pause the program at) on the `EntryPoint` which is the start of the `entry` function.
<br>
Click on `run`, to stop at that `breakpoint`.

![x32dbg entrypoint](screenshots/x32dbg_entrypoint.png)

Trying to debug `entry`, it was looping and looping a lot, I couldn't understand how it works.

But because I know there is a loop, in which the 3D object is drawn. I decided to return from `entry` function, as `entry` didn't seem to have anything with 3D.

Because clicking `execute until return` key, didn't seem to start the 3D.
I tried creating a `breakpoint` at the return instruction.

![return entry](screenshots/return_entry.png)

> In (1) is the return instruction.
<br>
> In (2) is the return address before executing entry. (returning, will return the execution to this address)

But, there was a surprise after executing `entry`. The return address has changed, and is now in `0x420000` which seems a very odd address, especially after seeing this address being used in the function.
<br>
So maybe `entry` just builds some code in `0x420000` then, transfers execution to it.

![return entry after](screenshots/return_entry_after.png)

After arriving at the return, stepping one instruction to go the built function.
<br>
Then, I used `x32dbg` `graph` function, to make the function more readable in the debugger.

Lets call this function `main`.

This is the graph:

> This graph is taken after the execution has completed `loop 1` (In a moment why is that.)

![graph documented](screenshots/graph_documented.png)

There are 3 main parts in this function.
- [Loop 1](#loop-1)
- [Initialization](#initialization)
    - [<0x4201ff> function](#0x4201ff-function)
    - [<0x4201a2> function](#0x4201a2-function)
- [Loop 2](#loop-2)

Before getting into analysing this function. If we tried to return from this function, it does not return and the 3D animation starts playing.
<br>
So, now we know that all the important things are inside this function, also because there are GUI and 3D related functions as shown in the graph.

### Loop 1

From the graph, `loop 1` is not only one loop, and rather more than one loop inside each other.

In loop 1, at the top right it checks for something. 
If `$ebp is not zero`, then it calls [MessageBoxA](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa) maybe to show error message then return.
<br>
So, its not important.

It's noticed that there is one `call` instruction in this loop which calls [LoadLibraryA](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya) function. (which loads a `.dll` file). And all other instructions are moving data around and XORing, shifting and other stuff.

Putting a breakpoint on the call instruction and after the loop (in order to stop), and continuing the program multiple times

![after loop 1](screenshots/after_loop_1.png)

`LoadLibraryA` is being called 3 times with:

- `user32`    -> Windows and other things
- `d3d9`      -> 3D DirectX
- `d3dx9_43`  -> 3D DirectX

And the other shifting and moving data, is maybe to get the members functions needed by this program.

> The reason the graph was taken after this loop is that, this loops 
initializes some function references related to the `dll`s loaded.
So if the graph taken after the loop, the names of the
functions will appear in the debugger.

### Initialization

In initialization phase (I called it `initialization` because it is called once only).

First, `0x4201ca` is being called.
<br>
Its a small function, that return `0xBf800000` after moving float data around
some addresses. (not sure what is the purpose of it).

![unknown function 1](screenshots/unknown_func_1.png)

Second, [Direct3DCreate9](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-direct3dcreate9) is being called with `0x20` as a version number to initialize IDirect3D9 interface object.

If the result `is not zero` it proceed.

I created this C-pseudocode code from the graph above. 

``` C
RECT rect;  // holds the data for window rect object

HWND handler = CreateWindowExA(
    0,
    "static",   // class name
    "demo",     // window name
    0x10CF0000, // pointer to style DWORD (not importnant)
    0,          // x 
    0,          // y
    0x320,      // width
    0x258,      // height
    0, 0, 0, 0);

// request the rect measurements of the rect, using positions
// top, bottom, right, left
GetWindowRect(handler, &rect);

// compute the position of the window to be in middle horizontally
$edi = (GetSystemMetrics(SM_CXSCREEN /* == 0*/) - rect.right) / 2;  
// compute the position of the window to be in middle vertically
$eax = (GetSystemMetrics(SM_CYSCREEN /* == 1*/) - rect.bottom) / 2;

setWindowPos(handler, 0, $edi, $eax, 0, 0, 0x5);    // sets the window in the middle of the screen
```

[CreateWindowExA](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindowexa)
<br>
[GetWindowRect](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect)
<br>
[RECT](https://docs.microsoft.com/en-us/windows/win32/api/windef/ns-windef-rect)
<br>
[GetSystemMetrics](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics)
<br>
[SetWindowPos](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos)

![create device function](screenshots/create_device_func.png)

Next, in the same big block.
<br>
A method inside IDirect3D9 is being called.
<br>
because it looks like it dereferenced `IDirect3D9 interface object` which was
located in `[ebp-4]` and what looked like a call to some kind of `v-table`.

After some research, after constructing `IDirect3D9 interface object` is being created, [CreateDevice](https://docs.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3d9-createdevice) is being called to create a 3D device which is used in drawing and rendering.
<br>
Also the number of arguments passed to this calling function match `CreateDevice`

``` C
IDirect3D9_object.CreateDevice(
    0,
    D3DDEVTYPE_HAL,     // == 1
    handler,            // from createWindowExA
    40,
    <ptr>,              // D3DPRESENT_PARAMETERS
    <ptr2>              // IDirect3DDevice9 result ptr
);
```

Lastly, before `loop 2` if the result of `createDevice` is not `0` it calls two functions:
- function at <`0x4201ff`>
- function at <`0x4201a2`>

When debugging normally, I couldn't find what these functions and the function inside `loop 2` does.

> during the competition I didn't solve it using this exact method, but something
related to `.pdb` files. I used [apitrace](https://apitrace.github.io)
(not used in this write-up).

During writing this write-up I learned about `.pdb` files, which are debug/symbols files and can be downloaded for `Microsoft dlls`.
<br>
And that x64/32dbg can be used to download these files during debugging.

From `Symbols` tab in x64/32dbg -> 
Right click any module -> 
click `Download Symbols for This Module`.

> You need to download symbols after `loop 1`, because 
these dlls are only loaded during `loop 1`.

After downloading the symbols trying to check `createDevice` call again.

![create device function after symbols](screenshots/create_device_func_symbols.png)

And its right there. NICE.

#### <0x4201ff> function
![0x4201ff function](screenshots/4201ff_func.png)

This is a straightforward function without jumps

First, it calls `0x4202ab` function. Looking through the method it appears that it 
initialized some kind of `mesh` object using
[D3DXCreateMeshFVF](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxcreatemeshfvf)
and other functions. So I called it `m_createMesh` and the results are stored
in global locations.

Interesting observation is that this method is called twice with different arguments.
> only captured the interesting argument that I understand.

1) NumFaces = 0x038( 56),  NumVertices = 0x01E( 30)
2) NumFaces = 0x10A(266),  NumVertices = 0x128(296)

There are **two** meshes inside this program, I guess the smaller one is for the logo,
And the large one might be for the **`flag`**, because it looks like a complex 3D mesh.
<br>
This is good progress, now we know that the `flag` might not text and rather 3D drawing but we still don't know why it's not drawn.

After that there is `4` calls to [IDirect3DDevice9::SetRenderState](https://docs.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3ddevice9-setrenderstate)
which are not very important to get the flag.

#### <0x4201a2> function

This is a very small function with only `2` function calls.

![0x4201a2 function part 1](screenshots/4201a2_func_part1.png)
![0x4201a2 function part 2](screenshots/4201a2_func_part2.png)

1) [IDirect3DDevice9::SetLight](https://docs.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3ddevice9-setlight)
2) [IDirect3DDevice9::LightEnable](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-lightenable)

These are not important for us to solve this challenge.

### Loop 2

In this loop there are only `2` function calls.

1) [<0x42038a> function](#<0x42038a>-function)
2) `GetAsyncKeyState(VK_ESCAPE /* 0x1B */)` to check for clicks for `ESC` key.

#### <0x42038a> function

Looks like this function only calls library functions/methods and does not do any calculation by itself.

This is the calls in this function in order without arguments:

- [IDirect3DDevice9::Clear](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-clear)
- [IDirect3DDevice9::BeginScene](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-beginscene)
- [IDirect3DDevice9::SetFVF](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-setfvf)
- [D3DXMatrixLookAtLH](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixlookatlh)
- [IDirect3DDevice9::SetTransform](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-settransform)
- [D3DXMatrixPerspectiveFovLH](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixperspectivefovlh)
- [IDirect3DDevice9::SetTransform](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-settransform)
- [D3DXMatrixTranslation](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixtranslation)
- [D3DXMatrixRotationY](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixrotationy)
- [D3DXMatrixRotationY](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixrotationy)
- [IDirect3DDevice9::SetMaterial](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-setmaterial)
- [IDirect3DDevice9::SetTransform](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-settransform)
- [ID3DXBaseMesh::DrawSubset](https://docs.microsoft.com/en-us/windows/win32/direct3d9/id3dxbasemesh--drawsubset)
Draw the first mesh (the small one).
- [D3DXMatrixMultiply](https://docs.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixmultiply)
- [IDirect3DDevice9::SetTransform](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-settransform)
Do some transformation to the screen view (camera?)
- [ID3DXBaseMesh::DrawSubset](https://docs.microsoft.com/en-us/windows/win32/direct3d9/id3dxbasemesh--drawsubset)
Draw the second mesh (the large one).
- [IDirect3DDevice9::EndScene](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-endscene)
- [IDirect3DDevice9::Present](https://docs.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-present)

Most of these are clear from the function name, and you can check the documentation of the others.
<br>
But I highlighted the ones that are related to the flag.

From this, it looks like that the flag is being drawn, but after transformation to hide it.

## Solution

After analysis, looks like there are `2` meshes in this program.
<br>
One for the logo, and one mostly for the flag. In drawing loop, it does some transformation (rotation), draws the logo, do some transformation again, then finally draw the flag.

The second transformation maybe it makes the drawing be outside the screen or make it rotate in a degree that we don't see it because its tickness is `0`.

The solution is just to disable the second transformation before drawing the flag.
<br>
One way of doing this is to replace the call instructions and its arguments with `NOP`s (no operation opcode).

![nops filling](screenshots/nops_filling.png)

After applying the patch. Run/continue execution.

This is the result (pause):

![flag rotation](screenshots/flag_rotation.png)

Then using `GIMP` or any tool to flip the image horizontally we get:

![flag rotation fixed](screenshots/flag_rotation_fixed.png)

If you want you can remove the logo as well using the same
method (`NOP`s) for better quality flag image:

![flag rotation no logo fixed](screenshots/flag_rotation_no_logo_fixed.png)

Flag is:

```
moar_pouetry@flare-on.com
```
