Memecat Battelstation
---

```
Welcome to the Sixth Flare-On Challenge! 

This is a simple game. Reverse engineer it to figure out what "weapon codes" you need to enter to defeat each of the two enemies and the victory screen will reveal the flag. Enter the flag here on this site to score and move on to the next level.

* This challenge is written in .NET. If you don't already have a favorite .NET reverse engineering tool I recommend dnSpy

** If you already solved the full version of this game at our booth at BlackHat  or the subsequent release on twitter, congratulations, enter the flag from the victory screen now to bypass this level.
```

```
$ file MemeCatBattlestation.exe
MemeCatBattlestation.exe: PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
```

- [Memecat Battelstation](#memecat-battelstation)
- [Introduction](#introduction)
- [Information collecting](#information-collecting)
- [Solution](#solution)

## Introduction

So this is the first Flare-on 2019 challenge.

Stated in the message that this is a DotNet executable as also confirmed by `file`.

Also in the message stated using `dnspy` tool which is a DotNet decompiler and debugger.

If flare-vm is installed it can be found in `FLARE\dotNET`, there are two types `dnspy-x86` which is for 32bit exe and `dnspy` which is for 64bit exe.

In our case the exe is 32bit so we are using `dnspy-x86`.

## Information collecting

Using `dnSpy`:

The main code is stored inside `MemeCatBattleStation` namespace.
which has 4 classes:
- `LogoForm`
- `Program`
- `Stage1Form`
- `Stage2Form`
- `VectoryForm`

`VectoryForm` seems very interesting.

inside it we see immediately `VictoryForm_Load` method:
``` C#
private void VictoryForm_Load(object sender, EventArgs e)
{
	byte[] array = new byte[]
    {
        //.... data trunked
    };
	byte[] bytes = Encoding.UTF8.GetBytes(this.Arsenal);
	for (int i = 0; i < array.Length; i++)
    {
		byte[] array2 = array;
		int num = i;
		array2[num] ^= bytes[i % bytes.Length];
	}
	this.flagLabel.Text = Encoding.UTF8.GetString(array);
}
```

This method, convert `Arsenal` String into byte[] then XOR it with `array`, and assigns the result to `flagLabel` text object in the form.

From this, `Arsenal` is the key to solve this challenge, And `Arsenal` is assigned in `Program.Main` method.

``` C#
private static void Main()
{
	/*
	... trunked
	*/
	Stage1Form stage1Form = new Stage1Form();
	Application.Run(stage1Form);
	if (stage1Form.WeaponCode == null)  // check 1
	{
		return;
	}
	Stage2Form stage2Form = new Stage2Form();
	stage2Form.Location = stage1Form.Location;
	Application.Run(stage2Form);
	if (stage2Form.WeaponCode == null)  // check 2
	{
		return;
	}
	Application.Run(new VictoryForm
	{
        // assignment of Arsenal
		Arsenal = string.Join(",", new string[]
		{
			stage2Form.WeaponCode,  // variables used in Arsenal
			stage1Form.WeaponCode   // we know these are not null based
                                    // based on check 1 and check 2
		}),
		Location = stage2Form.Location
	});
}
```
Important variables are
- Arsenal
- stage1Form.WeaponCode
- stage2Form.WeaponCode

## Solution

Using the same analysis on WeaponCode stage 1 and 2.
We get that all of them are assigned in method `FireButton_Click`:
``` C#
// Stage1Form
private void FireButton_Click(object sender, EventArgs e)
{
    // if value of WeaponCode if `true`
	if (this.codeTextBox.Text == "RAINBOW")
	{
		/*
		... trunked
		*/
		this.WeaponCode = this.codeTextBox.Text;
	}
	/*
	... trunked
	*/
}
```
From above, easily we can see that WeaponCode will be `"RAINBOW"` because it is the only place assigned.

``` C#
// Stage2Form
private void FireButton_Click(object sender, EventArgs e)
{
    // Same as above but not as easy as ==
    // so if this is `true` WeaponCode will be `codeTextBox.Text`
	if (this.isValidWeaponCode(this.codeTextBox.Text))
	{
		/*
		... trunked
		*/
		this.WeaponCode = this.codeTextBox.Text;
	}
	/*
	... trunked
	*/
}

// Check method
private bool isValidWeaponCode(string s)
{
	char[] array = s.ToCharArray();
	int length = s.Length;
    for (int i = 0; i < length; i++)
	{
	    char[] array2 = array;
		int num = i;
		array2[num] ^= 'A';
	}
	return array.SequenceEqual(new char[]
	{
		'\u0003', ' ', '&', '$', '-', '\u001e', '\u0002', ' ', '/', '/', '.', '/'
	});
}
```
- `array.SequenceEqual(other)` will return true if `array` and `other` are equal.

In order for `isValidWeaponCode` to return true, `(string s)` XORed with `'A'` should be equal to the `char array`.

XOR operation can be done again to reverse effect of previous XOR.
<br>
i.e.
`( 1 ^ 5 ) ^ 5 == 1`
<br>
using this we can retrieve the correct `string s`

``` C#
char[] result = new char[]
{
	'\u0003', ' ', '&', '$', '-', '\u001e', '\u0002', ' ', '/', '/', '.', '/'
};

for (int i = 0; i < result.Length; i++)
{
	result[i] ^= 'A';
}

string stage2pass = new string(result);
```

The final result of the above code is `Bagel_Cannon`.

Using all the above information.

``` C#
stage2Form.WeaponCode = "Bagel_Cannon";
stage1Form.WeaponCode = "RAINBOW";

Arsenal = "Bagel_Cannon,RAINBOW";
```

Now if we decoded the array in `VictoryForm_Load` using `Arsenal` we get
```
Kitteh_save_galixy@flare-on.com
```
