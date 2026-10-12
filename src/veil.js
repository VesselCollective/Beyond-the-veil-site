/* The living veil: a slow, iridescent silk rendered on the GPU.
   One small fragment shader, drawn at reduced resolution, paused when hidden.
   Falls back to the CSS background when WebGL or motion is unavailable. */
(function () {
  var canvas = document.querySelector('canvas.veil');
  if (!canvas) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false, powerPreference: 'low-power' });
  function fail() { canvas.classList.add('off'); document.documentElement.classList.add('no-veil'); }
  if (!gl) { fail(); return; }

  var vs = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var fs = [
    'precision mediump float;',
    'uniform vec2 r;uniform float t;uniform vec2 m;',
    'float h(vec2 p){',
    '  float v=sin(p.x*1.35+t*.32+sin(p.y*.9+t*.17)*1.6)*.6;',
    '  v+=sin(p.x*2.7-p.y*.8+t*.46+sin(p.x*.6-t*.22)*2.1)*.28;',
    '  v+=sin(p.y*2.1+p.x*.5-t*.27)*.2;',
    '  v+=sin((p.x+p.y)*4.3+t*.6)*.05;',
    '  return v;}',
    'void main(){',
    '  vec2 uv=gl_FragCoord.xy/r;',
    '  vec2 p=(gl_FragCoord.xy-.5*r)/min(r.x,r.y)*3.1;',
    '  vec2 d=p-m;float pull=exp(-dot(d,d)*2.)*.45;',
    '  vec2 q=p+vec2(0.,pull);',
    '  float e=.012;float c=h(q);',
    '  vec2 g=vec2(h(q+vec2(e,0.))-c,h(q+vec2(0.,e))-c)/e;',
    '  vec3 n=normalize(vec3(-g*.5,1.));',
    '  vec3 l=normalize(vec3(-.35,.55,.76));',
    '  float diff=max(dot(n,l),0.);',
    '  float spec=pow(max(dot(n,normalize(l+vec3(0.,0.,1.))),0.),60.);',
    '  float fres=pow(1.-n.z,1.6);',
    '  vec3 film=.5+.5*cos(6.2831*(fres*1.7+c*.22+t*.02+vec3(.0,.28,.62)));',
    '  vec3 col=vec3(.02,.022,.034)+diff*diff*vec3(.05,.052,.07)+spec*vec3(.55,.56,.64)+fres*film*vec3(.26,.24,.4);',
    '  float vig=smoothstep(1.3,.1,length((uv-vec2(.5,.66))*vec2(1.,1.2)));',
    '  col*=.35+.65*vig;',
    '  col=mix(col,vec3(.027,.031,.051),smoothstep(.42,0.,uv.y));',
    '  gl_FragColor=vec4(col,1.);}'
  ].join('\n');

  function sh(type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
  }
  var v = sh(gl.VERTEX_SHADER, vs), f = sh(gl.FRAGMENT_SHADER, fs);
  if (!v || !f) { fail(); return; }
  var prog = gl.createProgram(); gl.attachShader(prog, v); gl.attachShader(prog, f); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { fail(); return; }
  gl.useProgram(prog);
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  var uR = gl.getUniformLocation(prog, 'r'), uT = gl.getUniformLocation(prog, 't'), uM = gl.getUniformLocation(prog, 'm');

  var scale = 0.5, w = 0, h = 0;
  var mx = 0, my = 3, tx = 0, ty = 3; // pointer target, starts off-canvas
  function resize() {
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2) * scale;
    w = Math.max(1, Math.round(rect.width * dpr)); h = Math.max(1, Math.round(rect.height * dpr));
    canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h);
  }
  function toVeil(cx, cy) {
    var rect = canvas.getBoundingClientRect();
    var s = Math.min(rect.width, rect.height) / 2.2;
    tx = (cx - rect.left - rect.width / 2) / s;
    ty = -(cy - rect.top - rect.height / 2) / s;
  }
  window.addEventListener('pointermove', function (ev) { toVeil(ev.clientX, ev.clientY); }, { passive: true });
  window.addEventListener('resize', resize);
  resize();

  var visible = true, start = performance.now(), raf = 0, last = 0;
  function frame(now) {
    if (document.documentElement.classList.contains('past-hero') && now - last < 41) { raf = requestAnimationFrame(frame); return; }
    last = now;
    var tt = reduce ? 8 : (now - start) / 1000;
    mx += (tx - mx) * 0.04; my += (ty - my) * 0.04;
    gl.uniform2f(uR, w, h); gl.uniform1f(uT, tt); gl.uniform2f(uM, mx, my);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    canvas.classList.add('on');
    if (!reduce && visible && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function play() { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
  document.addEventListener('visibilitychange', function () { if (!document.hidden) play(); });
  play();
})();
