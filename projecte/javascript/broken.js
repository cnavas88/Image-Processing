function InpaintTelea2(width, height, image, mask, radius){
	if(!radius) radius = 5;

	var LARGE_VALUE = 1e6;
	var SMALL_VALUE = 1e-6;

	var size = width * height;
	var flag = new Uint8Array(size);
	var u = new Float32Array(size);
	
	for(var n = 0; n < size; n++){
		if(!mask[n]) continue;
		flag[n + 1] = flag[n] = flag[n - 1] = flag[n + width] = flag[n - width] = 1;
	}
	
	for(var n = 0; n < size; n++){
		flag[n] = (flag[n] * 2) - (mask[n] ^ flag[n])
		if(flag[n] == 2) // UNKNOWN
			u[n] = LARGE_VALUE;
	}


	var heap = new HeapQueue(function(a, b){ return a[0] - b[0] }) // sort by first thingy
	
	for(var n = 0; n < size; n++){
		if(flag[n] == 1) // BAND
			heap.push([u[n], n]);
	}
	
	var indices_centered = []
	for(var j = -radius; j <= radius; j++){
		var h = Math.floor(Math.sqrt(radius * radius - j * j))
		for(var i = -h; i <= h; i++)
			indices_centered.push(i + j * width);
	}

	function inpaint_point2(n){
		var Ia = 0, Jx = 0, Jy = 0, s = 1.0e-20;
		
		var t = u, f = flag;

		if(f[n + 1] != 2){
			if(f[n - 1] != 2){
				gradTX = (t[n + 1] - t[n - 1]) * 0.5
			}else{
				gradTX = t[n + 1] - t[n]
			}
		}else{
			if(f[n - 1] != 2){
				gradTX = t[n] - t[n - 1]
			}else{
				gradTX = 0
			}
		}
		if(f[n + width] != 2){
			if(f[n - width] != 2){
				gradTY = (t[n + width] - t[n - width]) * 0.5
			}else{
				gradTY = t[n + width] - t[n]
			}
		}else{
			if(f[n - width] != 2){
				gradTY = t[n] - t[n - width]
			}else{
				gradTY = 0
			}
		}


		var i = Math.floor(n / width),
			j = n % width;

		for(var ck = 0; ck < indices_centered.length; ck++){
			var nb = n + indices_centered[ck];

			var k = Math.floor(nb / width),
				l = nb % width;
			var ry = j - k,
				rx = j - l;

			var nm = nb; // less by one for some reason i dont know

			// var dst = 1 / Math.pow(rx * rx + ry * ry, )
			var dst = 1 / ((rx * rx + ry * ry) * Math.sqrt(rx * rx + ry * ry));
			var lev = 1 / (1 + Math.abs(t[nb] - t[n]))
			var dir = rx * gradTX + ry * gradTY;
			if(Math.abs(dir) <= 0.01) dir = 0.000001;
			var w = Math.abs(dst * lev * dir)

			if(f[nb + 1] != 2){
				if(f[nb - 1] != 2){
					gradIX = (image[nm + 1] - image[nm - 1]) * 2;
				}else{
					gradIX = image[nm + 1] - image[nm]
				}
			}else{
				if(f[nb - 1] != 2){
					gradIX = image[nm] - image[nm - 1]
				}else{
					gradIX = 0
				}
			}
			if(f[nb + width] != 2){
				if(f[nb - width] != 2){
					gradIY = (image[nm + width] - image[nm - width]) * 2
				}else{
					gradIY = image[nm + width] - image[nm]
				}
			}else{
				if(f[nb - width] != 2){
					gradIY = image[nm] - image[nm - width]
				}else{
					gradIY = 0
				}
			}

			Ia += w * image[nm]
			Jx -= w * gradIX * rx;
			Jy -= w * gradIY * ry;
			s += w;
		}	

		image[n] = Ia / s + (Jx + Jy)/(Math.sqrt(Jx * Jx + Jy * Jy) + 1e-20) + 0.5;

	}

	function FastMarching_solve(n1, n2){
		var t = u, f = flag;

		var sol, 
			a11 = t[n1], 
			a22 = t[n2], 
			m12 = Math.min(a11, a22);
		if(f[n1] != 2 /*INSIDE*/){
			if(f[n2] != 2){
				if(Math.abs(a11 - a22) >= 1){
					sol = 1 + m12
				}else{
					sol = (a11 + a22 + Math.sqrt(2 - (a11 - a22) * (a11 - a22))) * 0.5;
				}
			}else{
				sol = 1 + a11;
			}
		}else if(f[n2] != 2){
			sol = 1 + a22
		}else{
			sol = 1 + m12
		}
		return sol
	}

	while(heap.length){
		var n = heap.pop()[1];
		var j = n % width,
			i = Math.floor(n / width);
		flag[n] = 0; // KNOWN
		if(i <= 1 || j <= 1 || i >= height - 1 || j >= width - 1) continue;

		for(var k = 0; k < 4; k++){
			var nb = n + [-width, -1, width, 1][k];
			if(flag[nb] != 0){ // not KNOWN
				u[nb] = Math.min(FastMarching_solve(nb - width, nb - 1),
                                 FastMarching_solve(nb + width, nb - 1),
                                 FastMarching_solve(nb - width, nb + 1),
                                 FastMarching_solve(nb + width, nb + 1));
				if(flag[nb] == 2){ // UNKNOWN
					flag[nb] = 1; // BAND
					heap.push([u[nb], nb])
					inpaint_point2(nb)
				}
			}
		}
	}
	return image;
}

