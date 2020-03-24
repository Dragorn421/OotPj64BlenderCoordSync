// print exceptions
// (pj64 does not show stacktrace of uncaught exceptions...)
function handle(e)
{
	var lines = e.stack.split('\n');
	for(var i=0;i<lines.length;i++)
		console.log(lines[i]);
}

// incoming connection with all data loaded
function handleSocketData(socket, data) {
	try{
		console.log(data);
		var bin = new Uint8Array(data);
		switch(bin[0])
		{
		// find link coordinates
		case 1:
			/*
			Find link actor instance:
			for debug (n, firstactor*) [12][2] is at 0x80213C50
			see https://wiki.cloudmodding.com/oot/Global_Context_(Game)
			nextactor* is at offset 0x0124 in each actor struct
			actor struct is 0x014C bytes long for debug
			*/
			var position = [];// will store x,y,z,rx,ry,rz
			// target actor is type 2 (player)
			var n = mem.u32[0x80213C50 + 16];
			console.log('n');
			console.log(n);
			// actor address
			var actor = mem.u32[0x80213C50 + 16 + 4];
			// a loop is useless (expected n==1), apart from for debug
			// if ever there are more than one player-type actor
			for(var i=0;i<n;i++)
			{
				console.log('actor');
				console.log(actor.hex());
				var id = mem.u16[actor + 0];
				console.log('id');
				console.log(id);
				position.push(mem.float[actor + 0x0024]);//x
				position.push(mem.float[actor + 0x0024 + 4]);//y
				position.push(mem.float[actor + 0x0024 + 4 + 4]);//z
				position.push(mem.s16[actor + 0x00B4]);//rx
				position.push(mem.s16[actor + 0x00B4 + 2]);//ry
				position.push(mem.s16[actor + 0x00B4 + 2 + 2]);//rz
				// next (hopefully none)
				actor = mem.u32[actor + 0x0124];
			}
			// stringify data because no idea how to transfer float in js/python otherwise
			var str = '';
			for(var i=0;i<position.length;i++)
				str += position[i].toString() + ' ';
			console.log(str);
			socket.write(str+'\n');
			break;
		// set link coordinates
		case 2:
			// stringify and parse data
			var dataStr = '';
			for(var i=0;i<bin.length;i++)
				dataStr += String.fromCharCode(bin[i]);
			var parts = dataStr.substring(1).split(' ');
			var x = parseFloat(parts[0]);
			var y = parseFloat(parts[1]);
			var z = parseFloat(parts[2]);
			console.log('x');
			console.log(x);
			console.log('y');
			console.log(y);
			console.log('z');
			console.log(z);
			// find link actor instance
			var n = mem.u32[0x80213C50 + 16];
			console.log('n');
			console.log(n);
			var actor = mem.u32[0x80213C50 + 16 + 4];
			for(var i=0;i<n;i++)
			{
				console.log('actor');
				console.log(actor.hex());
				var id = mem.u16[actor + 0];
				console.log('id');
				console.log(id);
				/*
				bruteforce: update every pos_*, to bypass collision checks (names from z64ovl)
					fewer memory changes may be enough
				0x0008 pos_1
				0x0024 pos_2
				0x0038 pos_3
				0x0100 pos_4
				*/
				var offsets = [0x0008, 0x0024, 0x0038, 0x0100];
				for(var j=0;j<offsets.length;j++)
				{
					o = offsets[j];
					mem.float[actor + o] = x;
					mem.float[actor + o + 4] = y;
					mem.float[actor + o + 4 + 4] = z;
				}
				actor = mem.u32[actor + 0x0124];
			}
			break;
		}
	} catch(e) {
		handle(e);
	}
}

// listen on port 80
function handleSocket(socket)
{
	socket.on('data', function(data){handleSocketData(socket, data);});
}

var server = new Server({port: 80});
server.on('connection', handleSocket);
