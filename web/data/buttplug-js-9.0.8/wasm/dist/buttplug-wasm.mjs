let ye;
let __tla = (async () => {
  var _a;
  var O = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
  function Tt(n) {
    return n && n.__esModule && Object.prototype.hasOwnProperty.call(n, "default") ? n.default : n;
  }
  function ft(n) {
    if (n.__esModule) return n;
    var e = n.default;
    if (typeof e == "function") {
      var t = function r() {
        return this instanceof r ? Reflect.construct(e, arguments, this.constructor) : e.apply(this, arguments);
      };
      t.prototype = e.prototype;
    } else t = {};
    return Object.defineProperty(t, "__esModule", {
      value: true
    }), Object.keys(n).forEach(function(r) {
      var i = Object.getOwnPropertyDescriptor(n, r);
      Object.defineProperty(t, r, i.get ? i : {
        enumerable: true,
        get: function() {
          return n[r];
        }
      });
    }), t;
  }
  var dt = {}, We = {}, ve = {}, lt = {
    exports: {}
  };
  (function(n) {
    var e = Object.prototype.hasOwnProperty, t = "~";
    function r() {
    }
    Object.create && (r.prototype = /* @__PURE__ */ Object.create(null), new r().__proto__ || (t = false));
    function i(l, v, u) {
      this.fn = l, this.context = v, this.once = u || false;
    }
    function d(l, v, u, p, g) {
      if (typeof u != "function") throw new TypeError("The listener must be a function");
      var G = new i(u, p || l, g), B = t ? t + v : v;
      return l._events[B] ? l._events[B].fn ? l._events[B] = [
        l._events[B],
        G
      ] : l._events[B].push(G) : (l._events[B] = G, l._eventsCount++), l;
    }
    function c(l, v) {
      --l._eventsCount === 0 ? l._events = new r() : delete l._events[v];
    }
    function h() {
      this._events = new r(), this._eventsCount = 0;
    }
    h.prototype.eventNames = function() {
      var v = [], u, p;
      if (this._eventsCount === 0) return v;
      for (p in u = this._events) e.call(u, p) && v.push(t ? p.slice(1) : p);
      return Object.getOwnPropertySymbols ? v.concat(Object.getOwnPropertySymbols(u)) : v;
    }, h.prototype.listeners = function(v) {
      var u = t ? t + v : v, p = this._events[u];
      if (!p) return [];
      if (p.fn) return [
        p.fn
      ];
      for (var g = 0, G = p.length, B = new Array(G); g < G; g++) B[g] = p[g].fn;
      return B;
    }, h.prototype.listenerCount = function(v) {
      var u = t ? t + v : v, p = this._events[u];
      return p ? p.fn ? 1 : p.length : 0;
    }, h.prototype.emit = function(v, u, p, g, G, B) {
      var q = t ? t + v : v;
      if (!this._events[q]) return false;
      var m = this._events[q], F = arguments.length, $, I;
      if (m.fn) {
        switch (m.once && this.removeListener(v, m.fn, void 0, true), F) {
          case 1:
            return m.fn.call(m.context), true;
          case 2:
            return m.fn.call(m.context, u), true;
          case 3:
            return m.fn.call(m.context, u, p), true;
          case 4:
            return m.fn.call(m.context, u, p, g), true;
          case 5:
            return m.fn.call(m.context, u, p, g, G), true;
          case 6:
            return m.fn.call(m.context, u, p, g, G, B), true;
        }
        for (I = 1, $ = new Array(F - 1); I < F; I++) $[I - 1] = arguments[I];
        m.fn.apply(m.context, $);
      } else {
        var te = m.length, P;
        for (I = 0; I < te; I++) switch (m[I].once && this.removeListener(v, m[I].fn, void 0, true), F) {
          case 1:
            m[I].fn.call(m[I].context);
            break;
          case 2:
            m[I].fn.call(m[I].context, u);
            break;
          case 3:
            m[I].fn.call(m[I].context, u, p);
            break;
          case 4:
            m[I].fn.call(m[I].context, u, p, g);
            break;
          default:
            if (!$) for (P = 1, $ = new Array(F - 1); P < F; P++) $[P - 1] = arguments[P];
            m[I].fn.apply(m[I].context, $);
        }
      }
      return true;
    }, h.prototype.on = function(v, u, p) {
      return d(this, v, u, p, false);
    }, h.prototype.once = function(v, u, p) {
      return d(this, v, u, p, true);
    }, h.prototype.removeListener = function(v, u, p, g) {
      var G = t ? t + v : v;
      if (!this._events[G]) return this;
      if (!u) return c(this, G), this;
      var B = this._events[G];
      if (B.fn) B.fn === u && (!g || B.once) && (!p || B.context === p) && c(this, G);
      else {
        for (var q = 0, m = [], F = B.length; q < F; q++) (B[q].fn !== u || g && !B[q].once || p && B[q].context !== p) && m.push(B[q]);
        m.length ? this._events[G] = m.length === 1 ? m[0] : m : c(this, G);
      }
      return this;
    }, h.prototype.removeAllListeners = function(v) {
      var u;
      return v ? (u = t ? t + v : v, this._events[u] && c(this, u)) : (this._events = new r(), this._eventsCount = 0), this;
    }, h.prototype.off = h.prototype.removeListener, h.prototype.addListener = h.prototype.on, h.prefixed = t, h.EventEmitter = h, n.exports = h;
  })(lt);
  var Lt = lt.exports;
  const Qe = Tt(Lt), Pt = Object.freeze(Object.defineProperty({
    __proto__: null,
    EventEmitter: Qe,
    default: Qe
  }, Symbol.toStringTag, {
    value: "Module"
  })), ze = ft(Pt);
  Object.defineProperty(ve, "__esModule", {
    value: true
  });
  ve.ButtplugLogger = ve.LogMessage = ve.ButtplugLogLevel = void 0;
  const Bt = ze;
  var le;
  (function(n) {
    n[n.Off = 0] = "Off", n[n.Error = 1] = "Error", n[n.Warn = 2] = "Warn", n[n.Info = 3] = "Info", n[n.Debug = 4] = "Debug", n[n.Trace = 5] = "Trace";
  })(le || (ve.ButtplugLogLevel = le = {}));
  class ht {
    constructor(e, t) {
      const r = /* @__PURE__ */ new Date(), i = r.getHours(), d = r.getMinutes(), c = r.getSeconds();
      this.timestamp = `${i}:${d}:${c}`, this.logMessage = e, this.logLevel = t;
    }
    get Message() {
      return this.logMessage;
    }
    get LogLevel() {
      return this.logLevel;
    }
    get Timestamp() {
      return this.timestamp;
    }
    get FormattedMessage() {
      return `${le[this.logLevel]} : ${this.timestamp} : ${this.logMessage}`;
    }
  }
  ve.LogMessage = ht;
  class De extends Bt.EventEmitter {
    static get Logger() {
      return De.sLogger === void 0 && (De.sLogger = new De()), this.sLogger;
    }
    constructor() {
      super(), this.maximumConsoleLogLevel = le.Off, this.maximumEventLogLevel = le.Off;
    }
    get MaximumConsoleLogLevel() {
      return this.maximumConsoleLogLevel;
    }
    set MaximumConsoleLogLevel(e) {
      this.maximumConsoleLogLevel = e;
    }
    get MaximumEventLogLevel() {
      return this.maximumEventLogLevel;
    }
    set MaximumEventLogLevel(e) {
      this.maximumEventLogLevel = e;
    }
    Error(e) {
      this.AddLogMessage(e, le.Error);
    }
    Warn(e) {
      this.AddLogMessage(e, le.Warn);
    }
    Info(e) {
      this.AddLogMessage(e, le.Info);
    }
    Debug(e) {
      this.AddLogMessage(e, le.Debug);
    }
    Trace(e) {
      this.AddLogMessage(e, le.Trace);
    }
    AddLogMessage(e, t) {
      if (t > this.maximumEventLogLevel && t > this.maximumConsoleLogLevel) return;
      const r = new ht(e, t);
      t <= this.maximumConsoleLogLevel && console.log(r.FormattedMessage), t <= this.maximumEventLogLevel && this.emit("log", r);
    }
  }
  ve.ButtplugLogger = De;
  De.sLogger = void 0;
  var Be = {}, me = {}, R;
  (function(n) {
    n[n.PLAIN_TO_CLASS = 0] = "PLAIN_TO_CLASS", n[n.CLASS_TO_PLAIN = 1] = "CLASS_TO_PLAIN", n[n.CLASS_TO_CLASS = 2] = "CLASS_TO_CLASS";
  })(R || (R = {}));
  var xt = function() {
    function n() {
      this._typeMetadatas = /* @__PURE__ */ new Map(), this._transformMetadatas = /* @__PURE__ */ new Map(), this._exposeMetadatas = /* @__PURE__ */ new Map(), this._excludeMetadatas = /* @__PURE__ */ new Map(), this._ancestorsMap = /* @__PURE__ */ new Map();
    }
    return n.prototype.addTypeMetadata = function(e) {
      this._typeMetadatas.has(e.target) || this._typeMetadatas.set(e.target, /* @__PURE__ */ new Map()), this._typeMetadatas.get(e.target).set(e.propertyName, e);
    }, n.prototype.addTransformMetadata = function(e) {
      this._transformMetadatas.has(e.target) || this._transformMetadatas.set(e.target, /* @__PURE__ */ new Map()), this._transformMetadatas.get(e.target).has(e.propertyName) || this._transformMetadatas.get(e.target).set(e.propertyName, []), this._transformMetadatas.get(e.target).get(e.propertyName).push(e);
    }, n.prototype.addExposeMetadata = function(e) {
      this._exposeMetadatas.has(e.target) || this._exposeMetadatas.set(e.target, /* @__PURE__ */ new Map()), this._exposeMetadatas.get(e.target).set(e.propertyName, e);
    }, n.prototype.addExcludeMetadata = function(e) {
      this._excludeMetadatas.has(e.target) || this._excludeMetadatas.set(e.target, /* @__PURE__ */ new Map()), this._excludeMetadatas.get(e.target).set(e.propertyName, e);
    }, n.prototype.findTransformMetadatas = function(e, t, r) {
      return this.findMetadatas(this._transformMetadatas, e, t).filter(function(i) {
        return !i.options || i.options.toClassOnly === true && i.options.toPlainOnly === true ? true : i.options.toClassOnly === true ? r === R.CLASS_TO_CLASS || r === R.PLAIN_TO_CLASS : i.options.toPlainOnly === true ? r === R.CLASS_TO_PLAIN : true;
      });
    }, n.prototype.findExcludeMetadata = function(e, t) {
      return this.findMetadata(this._excludeMetadatas, e, t);
    }, n.prototype.findExposeMetadata = function(e, t) {
      return this.findMetadata(this._exposeMetadatas, e, t);
    }, n.prototype.findExposeMetadataByCustomName = function(e, t) {
      return this.getExposedMetadatas(e).find(function(r) {
        return r.options && r.options.name === t;
      });
    }, n.prototype.findTypeMetadata = function(e, t) {
      return this.findMetadata(this._typeMetadatas, e, t);
    }, n.prototype.getStrategy = function(e) {
      var t = this._excludeMetadatas.get(e), r = t && t.get(void 0), i = this._exposeMetadatas.get(e), d = i && i.get(void 0);
      return r && d || !r && !d ? "none" : r ? "excludeAll" : "exposeAll";
    }, n.prototype.getExposedMetadatas = function(e) {
      return this.getMetadata(this._exposeMetadatas, e);
    }, n.prototype.getExcludedMetadatas = function(e) {
      return this.getMetadata(this._excludeMetadatas, e);
    }, n.prototype.getExposedProperties = function(e, t) {
      return this.getExposedMetadatas(e).filter(function(r) {
        return !r.options || r.options.toClassOnly === true && r.options.toPlainOnly === true ? true : r.options.toClassOnly === true ? t === R.CLASS_TO_CLASS || t === R.PLAIN_TO_CLASS : r.options.toPlainOnly === true ? t === R.CLASS_TO_PLAIN : true;
      }).map(function(r) {
        return r.propertyName;
      });
    }, n.prototype.getExcludedProperties = function(e, t) {
      return this.getExcludedMetadatas(e).filter(function(r) {
        return !r.options || r.options.toClassOnly === true && r.options.toPlainOnly === true ? true : r.options.toClassOnly === true ? t === R.CLASS_TO_CLASS || t === R.PLAIN_TO_CLASS : r.options.toPlainOnly === true ? t === R.CLASS_TO_PLAIN : true;
      }).map(function(r) {
        return r.propertyName;
      });
    }, n.prototype.clear = function() {
      this._typeMetadatas.clear(), this._exposeMetadatas.clear(), this._excludeMetadatas.clear(), this._ancestorsMap.clear();
    }, n.prototype.getMetadata = function(e, t) {
      var r = e.get(t), i;
      r && (i = Array.from(r.values()).filter(function(p) {
        return p.propertyName !== void 0;
      }));
      for (var d = [], c = 0, h = this.getAncestors(t); c < h.length; c++) {
        var l = h[c], v = e.get(l);
        if (v) {
          var u = Array.from(v.values()).filter(function(p) {
            return p.propertyName !== void 0;
          });
          d.push.apply(d, u);
        }
      }
      return d.concat(i || []);
    }, n.prototype.findMetadata = function(e, t, r) {
      var i = e.get(t);
      if (i) {
        var d = i.get(r);
        if (d) return d;
      }
      for (var c = 0, h = this.getAncestors(t); c < h.length; c++) {
        var l = h[c], v = e.get(l);
        if (v) {
          var u = v.get(r);
          if (u) return u;
        }
      }
    }, n.prototype.findMetadatas = function(e, t, r) {
      var i = e.get(t), d;
      i && (d = i.get(r));
      for (var c = [], h = 0, l = this.getAncestors(t); h < l.length; h++) {
        var v = l[h], u = e.get(v);
        u && u.has(r) && c.push.apply(c, u.get(r));
      }
      return c.slice().reverse().concat((d || []).slice().reverse());
    }, n.prototype.getAncestors = function(e) {
      if (!e) return [];
      if (!this._ancestorsMap.has(e)) {
        for (var t = [], r = Object.getPrototypeOf(e.prototype.constructor); typeof r.prototype < "u"; r = Object.getPrototypeOf(r.prototype.constructor)) t.push(r);
        this._ancestorsMap.set(e, t);
      }
      return this._ancestorsMap.get(e);
    }, n;
  }(), V = new xt();
  function Nt() {
    if (typeof globalThis < "u") return globalThis;
    if (typeof global < "u") return global;
    if (typeof window < "u") return window;
    if (typeof self < "u") return self;
  }
  function jt(n) {
    return n !== null && typeof n == "object" && typeof n.then == "function";
  }
  var st = function(n, e, t) {
    if (t || arguments.length === 2) for (var r = 0, i = e.length, d; r < i; r++) (d || !(r in e)) && (d || (d = Array.prototype.slice.call(e, 0, r)), d[r] = e[r]);
    return n.concat(d || Array.prototype.slice.call(e));
  };
  function Ft(n) {
    var e = new n();
    return !(e instanceof Set) && !("push" in e) ? [] : e;
  }
  var Oe = function() {
    function n(e, t) {
      this.transformationType = e, this.options = t, this.recursionStack = /* @__PURE__ */ new Set();
    }
    return n.prototype.transform = function(e, t, r, i, d, c) {
      var h = this;
      if (c === void 0 && (c = 0), Array.isArray(t) || t instanceof Set) {
        var l = i && this.transformationType === R.PLAIN_TO_CLASS ? Ft(i) : [];
        return t.forEach(function(m, F) {
          var $ = e ? e[F] : void 0;
          if (!h.options.enableCircularCheck || !h.isCircular(m)) {
            var I = void 0;
            if (typeof r != "function" && r && r.options && r.options.discriminator && r.options.discriminator.property && r.options.discriminator.subTypes) {
              if (h.transformationType === R.PLAIN_TO_CLASS) {
                I = r.options.discriminator.subTypes.find(function(ae) {
                  return ae.name === m[r.options.discriminator.property];
                });
                var te = {
                  newObject: l,
                  object: m,
                  property: void 0
                }, P = r.typeFunction(te);
                I === void 0 ? I = P : I = I.value, r.options.keepDiscriminatorProperty || delete m[r.options.discriminator.property];
              }
              h.transformationType === R.CLASS_TO_CLASS && (I = m.constructor), h.transformationType === R.CLASS_TO_PLAIN && (m[r.options.discriminator.property] = r.options.discriminator.subTypes.find(function(ae) {
                return ae.value === m.constructor;
              }).name);
            } else I = r;
            var Y = h.transform($, m, I, void 0, m instanceof Map, c + 1);
            l instanceof Set ? l.add(Y) : l.push(Y);
          } else h.transformationType === R.CLASS_TO_CLASS && (l instanceof Set ? l.add(m) : l.push(m));
        }), l;
      } else {
        if (r === String && !d) return t == null ? t : String(t);
        if (r === Number && !d) return t == null ? t : Number(t);
        if (r === Boolean && !d) return t == null ? t : !!t;
        if ((r === Date || t instanceof Date) && !d) return t instanceof Date ? new Date(t.valueOf()) : t == null ? t : new Date(t);
        if (Nt().Buffer && (r === Buffer || t instanceof Buffer) && !d) return t == null ? t : Buffer.from(t);
        if (jt(t) && !d) return new Promise(function(m, F) {
          t.then(function($) {
            return m(h.transform(void 0, $, r, void 0, void 0, c + 1));
          }, F);
        });
        if (!d && t !== null && typeof t == "object" && typeof t.then == "function") return t;
        if (typeof t == "object" && t !== null) {
          !r && t.constructor !== Object && (!Array.isArray(t) && t.constructor === Array || (r = t.constructor)), !r && e && (r = e.constructor), this.options.enableCircularCheck && this.recursionStack.add(t);
          var v = this.getKeys(r, t, d), u = e || {};
          !e && (this.transformationType === R.PLAIN_TO_CLASS || this.transformationType === R.CLASS_TO_CLASS) && (d ? u = /* @__PURE__ */ new Map() : r ? u = new r() : u = {});
          for (var p = function(m) {
            if (m === "__proto__" || m === "constructor") return "continue";
            var F = m, $ = m, I = m;
            if (!g.options.ignoreDecorators && r) {
              if (g.transformationType === R.PLAIN_TO_CLASS) {
                var te = V.findExposeMetadataByCustomName(r, m);
                te && (I = te.propertyName, $ = te.propertyName);
              } else if (g.transformationType === R.CLASS_TO_PLAIN || g.transformationType === R.CLASS_TO_CLASS) {
                var te = V.findExposeMetadata(r, m);
                te && te.options && te.options.name && ($ = te.options.name);
              }
            }
            var P = void 0;
            g.transformationType === R.PLAIN_TO_CLASS ? P = t[F] : t instanceof Map ? P = t.get(F) : t[F] instanceof Function ? P = t[F]() : P = t[F];
            var Y = void 0, ae = P instanceof Map;
            if (r && d) Y = r;
            else if (r) {
              var W = V.findTypeMetadata(r, I);
              if (W) {
                var Ce = {
                  newObject: u,
                  object: t,
                  property: I
                }, Se = W.typeFunction ? W.typeFunction(Ce) : W.reflectedType;
                W.options && W.options.discriminator && W.options.discriminator.property && W.options.discriminator.subTypes ? t[F] instanceof Array ? Y = W : (g.transformationType === R.PLAIN_TO_CLASS && (Y = W.options.discriminator.subTypes.find(function(ne) {
                  if (P && P instanceof Object && W.options.discriminator.property in P) return ne.name === P[W.options.discriminator.property];
                }), Y === void 0 ? Y = Se : Y = Y.value, W.options.keepDiscriminatorProperty || P && P instanceof Object && W.options.discriminator.property in P && delete P[W.options.discriminator.property]), g.transformationType === R.CLASS_TO_CLASS && (Y = P.constructor), g.transformationType === R.CLASS_TO_PLAIN && P && (P[W.options.discriminator.property] = W.options.discriminator.subTypes.find(function(ne) {
                  return ne.value === P.constructor;
                }).name)) : Y = Se, ae = ae || W.reflectedType === Map;
              } else if (g.options.targetMaps) g.options.targetMaps.filter(function(ne) {
                return ne.target === r && !!ne.properties[I];
              }).forEach(function(ne) {
                return Y = ne.properties[I];
              });
              else if (g.options.enableImplicitConversion && g.transformationType === R.PLAIN_TO_CLASS) {
                var Me = Reflect.getMetadata("design:type", r.prototype, I);
                Me && (Y = Me);
              }
            }
            var Ee = Array.isArray(t[F]) ? g.getReflectedType(r, I) : void 0, he = e ? e[F] : void 0;
            if (u.constructor.prototype) {
              var we = Object.getOwnPropertyDescriptor(u.constructor.prototype, $);
              if ((g.transformationType === R.PLAIN_TO_CLASS || g.transformationType === R.CLASS_TO_CLASS) && (we && !we.set || u[$] instanceof Function)) return "continue";
            }
            if (!g.options.enableCircularCheck || !g.isCircular(P)) {
              var ce = g.transformationType === R.PLAIN_TO_CLASS ? $ : m, k = void 0;
              g.transformationType === R.CLASS_TO_PLAIN ? (k = t[ce], k = g.applyCustomTransformations(k, r, ce, t, g.transformationType), k = t[ce] === k ? P : k, k = g.transform(he, k, Y, Ee, ae, c + 1)) : P === void 0 && g.options.exposeDefaultValues ? k = u[$] : (k = g.transform(he, P, Y, Ee, ae, c + 1), k = g.applyCustomTransformations(k, r, ce, t, g.transformationType)), (k !== void 0 || g.options.exposeUnsetFields) && (u instanceof Map ? u.set($, k) : u[$] = k);
            } else if (g.transformationType === R.CLASS_TO_CLASS) {
              var k = P;
              k = g.applyCustomTransformations(k, r, m, t, g.transformationType), (k !== void 0 || g.options.exposeUnsetFields) && (u instanceof Map ? u.set($, k) : u[$] = k);
            }
          }, g = this, G = 0, B = v; G < B.length; G++) {
            var q = B[G];
            p(q);
          }
          return this.options.enableCircularCheck && this.recursionStack.delete(t), u;
        } else return t;
      }
    }, n.prototype.applyCustomTransformations = function(e, t, r, i, d) {
      var c = this, h = V.findTransformMetadatas(t, r, this.transformationType);
      return this.options.version !== void 0 && (h = h.filter(function(l) {
        return l.options ? c.checkVersion(l.options.since, l.options.until) : true;
      })), this.options.groups && this.options.groups.length ? h = h.filter(function(l) {
        return l.options ? c.checkGroups(l.options.groups) : true;
      }) : h = h.filter(function(l) {
        return !l.options || !l.options.groups || !l.options.groups.length;
      }), h.forEach(function(l) {
        e = l.transformFn({
          value: e,
          key: r,
          obj: i,
          type: d,
          options: c.options
        });
      }), e;
    }, n.prototype.isCircular = function(e) {
      return this.recursionStack.has(e);
    }, n.prototype.getReflectedType = function(e, t) {
      if (e) {
        var r = V.findTypeMetadata(e, t);
        return r ? r.reflectedType : void 0;
      }
    }, n.prototype.getKeys = function(e, t, r) {
      var i = this, d = V.getStrategy(e);
      d === "none" && (d = this.options.strategy || "exposeAll");
      var c = [];
      if ((d === "exposeAll" || r) && (t instanceof Map ? c = Array.from(t.keys()) : c = Object.keys(t)), r) return c;
      if (this.options.ignoreDecorators && this.options.excludeExtraneousValues && e) {
        var h = V.getExposedProperties(e, this.transformationType), l = V.getExcludedProperties(e, this.transformationType);
        c = st(st([], h, true), l, true);
      }
      if (!this.options.ignoreDecorators && e) {
        var h = V.getExposedProperties(e, this.transformationType);
        this.transformationType === R.PLAIN_TO_CLASS && (h = h.map(function(p) {
          var g = V.findExposeMetadata(e, p);
          return g && g.options && g.options.name ? g.options.name : p;
        })), this.options.excludeExtraneousValues ? c = h : c = c.concat(h);
        var v = V.getExcludedProperties(e, this.transformationType);
        v.length > 0 && (c = c.filter(function(p) {
          return !v.includes(p);
        })), this.options.version !== void 0 && (c = c.filter(function(p) {
          var g = V.findExposeMetadata(e, p);
          return !g || !g.options ? true : i.checkVersion(g.options.since, g.options.until);
        })), this.options.groups && this.options.groups.length ? c = c.filter(function(p) {
          var g = V.findExposeMetadata(e, p);
          return !g || !g.options ? true : i.checkGroups(g.options.groups);
        }) : c = c.filter(function(p) {
          var g = V.findExposeMetadata(e, p);
          return !g || !g.options || !g.options.groups || !g.options.groups.length;
        });
      }
      return this.options.excludePrefixes && this.options.excludePrefixes.length && (c = c.filter(function(u) {
        return i.options.excludePrefixes.every(function(p) {
          return u.substr(0, p.length) !== p;
        });
      })), c = c.filter(function(u, p, g) {
        return g.indexOf(u) === p;
      }), c;
    }, n.prototype.checkVersion = function(e, t) {
      var r = true;
      return r && e && (r = this.options.version >= e), r && t && (r = this.options.version < t), r;
    }, n.prototype.checkGroups = function(e) {
      return e ? this.options.groups.some(function(t) {
        return e.includes(t);
      }) : true;
    }, n;
  }(), Ae = {
    enableCircularCheck: false,
    enableImplicitConversion: false,
    excludeExtraneousValues: false,
    excludePrefixes: void 0,
    exposeDefaultValues: false,
    exposeUnsetFields: true,
    groups: void 0,
    ignoreDecorators: false,
    strategy: void 0,
    targetMaps: void 0,
    version: void 0
  }, oe = function() {
    return oe = Object.assign || function(n) {
      for (var e, t = 1, r = arguments.length; t < r; t++) {
        e = arguments[t];
        for (var i in e) Object.prototype.hasOwnProperty.call(e, i) && (n[i] = e[i]);
      }
      return n;
    }, oe.apply(this, arguments);
  }, xe = function() {
    function n() {
    }
    return n.prototype.instanceToPlain = function(e, t) {
      var r = new Oe(R.CLASS_TO_PLAIN, oe(oe({}, Ae), t));
      return r.transform(void 0, e, void 0, void 0, void 0, void 0);
    }, n.prototype.classToPlainFromExist = function(e, t, r) {
      var i = new Oe(R.CLASS_TO_PLAIN, oe(oe({}, Ae), r));
      return i.transform(t, e, void 0, void 0, void 0, void 0);
    }, n.prototype.plainToInstance = function(e, t, r) {
      var i = new Oe(R.PLAIN_TO_CLASS, oe(oe({}, Ae), r));
      return i.transform(void 0, t, e, void 0, void 0, void 0);
    }, n.prototype.plainToClassFromExist = function(e, t, r) {
      var i = new Oe(R.PLAIN_TO_CLASS, oe(oe({}, Ae), r));
      return i.transform(e, t, void 0, void 0, void 0, void 0);
    }, n.prototype.instanceToInstance = function(e, t) {
      var r = new Oe(R.CLASS_TO_CLASS, oe(oe({}, Ae), t));
      return r.transform(void 0, e, void 0, void 0, void 0, void 0);
    }, n.prototype.classToClassFromExist = function(e, t, r) {
      var i = new Oe(R.CLASS_TO_CLASS, oe(oe({}, Ae), r));
      return i.transform(t, e, void 0, void 0, void 0, void 0);
    }, n.prototype.serialize = function(e, t) {
      return JSON.stringify(this.instanceToPlain(e, t));
    }, n.prototype.deserialize = function(e, t, r) {
      var i = JSON.parse(t);
      return this.plainToInstance(e, i, r);
    }, n.prototype.deserializeArray = function(e, t, r) {
      var i = JSON.parse(t);
      return this.plainToInstance(e, i, r);
    }, n;
  }();
  function $t(n) {
    return n === void 0 && (n = {}), function(e, t) {
      V.addExcludeMetadata({
        target: e instanceof Function ? e : e.constructor,
        propertyName: t,
        options: n
      });
    };
  }
  function Gt(n) {
    return n === void 0 && (n = {}), function(e, t) {
      V.addExposeMetadata({
        target: e instanceof Function ? e : e.constructor,
        propertyName: t,
        options: n
      });
    };
  }
  function kt(n) {
    return function(e, t, r) {
      var i = new xe(), d = r.value;
      r.value = function() {
        for (var c = [], h = 0; h < arguments.length; h++) c[h] = arguments[h];
        var l = d.apply(this, c), v = !!l && (typeof l == "object" || typeof l == "function") && typeof l.then == "function";
        return v ? l.then(function(u) {
          return i.instanceToInstance(u, n);
        }) : i.instanceToInstance(l, n);
      };
    };
  }
  function Ut(n) {
    return function(e, t, r) {
      var i = new xe(), d = r.value;
      r.value = function() {
        for (var c = [], h = 0; h < arguments.length; h++) c[h] = arguments[h];
        var l = d.apply(this, c), v = !!l && (typeof l == "object" || typeof l == "function") && typeof l.then == "function";
        return v ? l.then(function(u) {
          return i.instanceToPlain(u, n);
        }) : i.instanceToPlain(l, n);
      };
    };
  }
  function Wt(n, e) {
    return function(t, r, i) {
      var d = new xe(), c = i.value;
      i.value = function() {
        for (var h = [], l = 0; l < arguments.length; l++) h[l] = arguments[l];
        var v = c.apply(this, h), u = !!v && (typeof v == "object" || typeof v == "function") && typeof v.then == "function";
        return u ? v.then(function(p) {
          return d.plainToInstance(n, p, e);
        }) : d.plainToInstance(n, v, e);
      };
    };
  }
  function zt(n, e) {
    return e === void 0 && (e = {}), function(t, r) {
      V.addTransformMetadata({
        target: t.constructor,
        propertyName: r,
        transformFn: n,
        options: e
      });
    };
  }
  function qt(n, e) {
    return e === void 0 && (e = {}), function(t, r) {
      var i = Reflect.getMetadata("design:type", t, r);
      V.addTypeMetadata({
        target: t.constructor,
        propertyName: r,
        reflectedType: i,
        typeFunction: n,
        options: e
      });
    };
  }
  var de = new xe();
  function Jt(n, e) {
    return de.instanceToPlain(n, e);
  }
  function Yt(n, e) {
    return de.instanceToPlain(n, e);
  }
  function Ht(n, e, t) {
    return de.classToPlainFromExist(n, e, t);
  }
  function Xt(n, e, t) {
    return de.plainToInstance(n, e, t);
  }
  function Zt(n, e, t) {
    return de.plainToInstance(n, e, t);
  }
  function Qt(n, e, t) {
    return de.plainToClassFromExist(n, e, t);
  }
  function Kt(n, e) {
    return de.instanceToInstance(n, e);
  }
  function Vt(n, e, t) {
    return de.classToClassFromExist(n, e, t);
  }
  function en(n, e) {
    return de.serialize(n, e);
  }
  function tn(n, e, t) {
    return de.deserialize(n, e, t);
  }
  function nn(n, e, t) {
    return de.deserializeArray(n, e, t);
  }
  const rn = Object.freeze(Object.defineProperty({
    __proto__: null,
    ClassTransformer: xe,
    Exclude: $t,
    Expose: Gt,
    Transform: zt,
    TransformInstanceToInstance: kt,
    TransformInstanceToPlain: Ut,
    TransformPlainToInstance: Wt,
    get TransformationType() {
      return R;
    },
    Type: qt,
    classToClassFromExist: Vt,
    classToPlain: Jt,
    classToPlainFromExist: Ht,
    deserialize: tn,
    deserializeArray: nn,
    instanceToInstance: Kt,
    instanceToPlain: Yt,
    plainToClass: Xt,
    plainToClassFromExist: Qt,
    plainToInstance: Zt,
    serialize: en
  }, Symbol.toStringTag, {
    value: "Module"
  })), pt = ft(rn);
  var ot;
  (function(n) {
    (function(e) {
      var t = typeof globalThis == "object" ? globalThis : typeof O == "object" ? O : typeof self == "object" ? self : typeof this == "object" ? this : h(), r = i(n);
      typeof t.Reflect < "u" && (r = i(t.Reflect, r)), e(r, t), typeof t.Reflect > "u" && (t.Reflect = n);
      function i(l, v) {
        return function(u, p) {
          Object.defineProperty(l, u, {
            configurable: true,
            writable: true,
            value: p
          }), v && v(u, p);
        };
      }
      function d() {
        try {
          return Function("return this;")();
        } catch {
        }
      }
      function c() {
        try {
          return (0, eval)("(function() { return this; })()");
        } catch {
        }
      }
      function h() {
        return d() || c();
      }
    })(function(e, t) {
      var r = Object.prototype.hasOwnProperty, i = typeof Symbol == "function", d = i && typeof Symbol.toPrimitive < "u" ? Symbol.toPrimitive : "@@toPrimitive", c = i && typeof Symbol.iterator < "u" ? Symbol.iterator : "@@iterator", h = typeof Object.create == "function", l = {
        __proto__: []
      } instanceof Array, v = !h && !l, u = {
        create: h ? function() {
          return Xe(/* @__PURE__ */ Object.create(null));
        } : l ? function() {
          return Xe({
            __proto__: null
          });
        } : function() {
          return Xe({});
        },
        has: v ? function(s, o) {
          return r.call(s, o);
        } : function(s, o) {
          return o in s;
        },
        get: v ? function(s, o) {
          return r.call(s, o) ? s[o] : void 0;
        } : function(s, o) {
          return s[o];
        }
      }, p = Object.getPrototypeOf(Function), g = typeof Map == "function" && typeof Map.prototype.entries == "function" ? Map : Ot(), G = typeof Set == "function" && typeof Set.prototype.entries == "function" ? Set : At(), B = typeof WeakMap == "function" ? WeakMap : Dt(), q = i ? Symbol.for("@reflect-metadata:registry") : void 0, m = wt(), F = bt(m);
      function $(s, o, a, _) {
        if (A(a)) {
          if (!x(s)) throw new TypeError();
          if (!Z(o)) throw new TypeError();
          return Ee(s, o);
        } else {
          if (!x(s)) throw new TypeError();
          if (!J(o)) throw new TypeError();
          if (!J(_) && !A(_) && !pe(_)) throw new TypeError();
          return pe(_) && (_ = void 0), a = E(a), he(s, o, a, _);
        }
      }
      e("decorate", $);
      function I(s, o) {
        function a(_, D) {
          if (!J(_)) throw new TypeError();
          if (!A(D) && !ie(D)) throw new TypeError();
          Re(s, o, _, D);
        }
        return a;
      }
      e("metadata", I);
      function te(s, o, a, _) {
        if (!J(a)) throw new TypeError();
        return A(_) || (_ = E(_)), Re(s, o, a, _);
      }
      e("defineMetadata", te);
      function P(s, o, a) {
        if (!J(o)) throw new TypeError();
        return A(a) || (a = E(a)), we(s, o, a);
      }
      e("hasMetadata", P);
      function Y(s, o, a) {
        if (!J(o)) throw new TypeError();
        return A(a) || (a = E(a)), ce(s, o, a);
      }
      e("hasOwnMetadata", Y);
      function ae(s, o, a) {
        if (!J(o)) throw new TypeError();
        return A(a) || (a = E(a)), k(s, o, a);
      }
      e("getMetadata", ae);
      function W(s, o, a) {
        if (!J(o)) throw new TypeError();
        return A(a) || (a = E(a)), ne(s, o, a);
      }
      e("getOwnMetadata", W);
      function Ce(s, o) {
        if (!J(s)) throw new TypeError();
        return A(o) || (o = E(o)), be(s, o);
      }
      e("getMetadataKeys", Ce);
      function Se(s, o) {
        if (!J(s)) throw new TypeError();
        return A(o) || (o = E(o)), Te(s, o);
      }
      e("getOwnMetadataKeys", Se);
      function Me(s, o, a) {
        if (!J(o)) throw new TypeError();
        if (A(a) || (a = E(a)), !J(o)) throw new TypeError();
        A(a) || (a = E(a));
        var _ = Pe(o, a, false);
        return A(_) ? false : _.OrdinaryDeleteMetadata(s, o, a);
      }
      e("deleteMetadata", Me);
      function Ee(s, o) {
        for (var a = s.length - 1; a >= 0; --a) {
          var _ = s[a], D = _(o);
          if (!A(D) && !pe(D)) {
            if (!Z(D)) throw new TypeError();
            o = D;
          }
        }
        return o;
      }
      function he(s, o, a, _) {
        for (var D = s.length - 1; D >= 0; --D) {
          var H = s[D], Q = H(o, a, _);
          if (!A(Q) && !pe(Q)) {
            if (!J(Q)) throw new TypeError();
            _ = Q;
          }
        }
        return _;
      }
      function we(s, o, a) {
        var _ = ce(s, o, a);
        if (_) return true;
        var D = He(o);
        return pe(D) ? false : we(s, D, a);
      }
      function ce(s, o, a) {
        var _ = Pe(o, a, false);
        return A(_) ? false : f(_.OrdinaryHasOwnMetadata(s, o, a));
      }
      function k(s, o, a) {
        var _ = ce(s, o, a);
        if (_) return ne(s, o, a);
        var D = He(o);
        if (!pe(D)) return k(s, D, a);
      }
      function ne(s, o, a) {
        var _ = Pe(o, a, false);
        if (!A(_)) return _.OrdinaryGetOwnMetadata(s, o, a);
      }
      function Re(s, o, a, _) {
        var D = Pe(a, _, true);
        D.OrdinaryDefineOwnMetadata(s, o, a, _);
      }
      function be(s, o) {
        var a = Te(s, o), _ = He(s);
        if (_ === null) return a;
        var D = be(_, o);
        if (D.length <= 0) return a;
        if (a.length <= 0) return D;
        for (var H = new G(), Q = [], T = 0, y = a; T < y.length; T++) {
          var M = y[T], w = H.has(M);
          w || (H.add(M), Q.push(M));
        }
        for (var b = 0, L = D; b < L.length; b++) {
          var M = L[b], w = H.has(M);
          w || (H.add(M), Q.push(M));
        }
        return Q;
      }
      function Te(s, o) {
        var a = Pe(s, o, false);
        return a ? a.OrdinaryOwnMetadataKeys(s, o) : [];
      }
      function Le(s) {
        if (s === null) return 1;
        switch (typeof s) {
          case "undefined":
            return 0;
          case "boolean":
            return 2;
          case "string":
            return 3;
          case "symbol":
            return 4;
          case "number":
            return 5;
          case "object":
            return s === null ? 1 : 6;
          default:
            return 6;
        }
      }
      function A(s) {
        return s === void 0;
      }
      function pe(s) {
        return s === null;
      }
      function $e(s) {
        return typeof s == "symbol";
      }
      function J(s) {
        return typeof s == "object" ? s !== null : typeof s == "function";
      }
      function Ge(s, o) {
        switch (Le(s)) {
          case 0:
            return s;
          case 1:
            return s;
          case 2:
            return s;
          case 3:
            return s;
          case 4:
            return s;
          case 5:
            return s;
        }
        var a = "string", _ = Ve(s, d);
        if (_ !== void 0) {
          var D = _.call(s, a);
          if (J(D)) throw new TypeError();
          return D;
        }
        return S(s);
      }
      function S(s, o) {
        var a, _, D;
        {
          var H = s.toString;
          if (N(H)) {
            var _ = H.call(s);
            if (!J(_)) return _;
          }
          var a = s.valueOf;
          if (N(a)) {
            var _ = a.call(s);
            if (!J(_)) return _;
          }
        }
        throw new TypeError();
      }
      function f(s) {
        return !!s;
      }
      function C(s) {
        return "" + s;
      }
      function E(s) {
        var o = Ge(s);
        return $e(o) ? o : C(o);
      }
      function x(s) {
        return Array.isArray ? Array.isArray(s) : s instanceof Object ? s instanceof Array : Object.prototype.toString.call(s) === "[object Array]";
      }
      function N(s) {
        return typeof s == "function";
      }
      function Z(s) {
        return typeof s == "function";
      }
      function ie(s) {
        switch (Le(s)) {
          case 3:
            return true;
          case 4:
            return true;
          default:
            return false;
        }
      }
      function Ye(s, o) {
        return s === o || s !== s && o !== o;
      }
      function Ve(s, o) {
        var a = s[o];
        if (a != null) {
          if (!N(a)) throw new TypeError();
          return a;
        }
      }
      function et(s) {
        var o = Ve(s, c);
        if (!N(o)) throw new TypeError();
        var a = o.call(s);
        if (!J(a)) throw new TypeError();
        return a;
      }
      function tt(s) {
        return s.value;
      }
      function nt(s) {
        var o = s.next();
        return o.done ? false : o;
      }
      function rt(s) {
        var o = s.return;
        o && o.call(s);
      }
      function He(s) {
        var o = Object.getPrototypeOf(s);
        if (typeof s != "function" || s === p || o !== p) return o;
        var a = s.prototype, _ = a && Object.getPrototypeOf(a);
        if (_ == null || _ === Object.prototype) return o;
        var D = _.constructor;
        return typeof D != "function" || D === s ? o : D;
      }
      function Et() {
        var s;
        !A(q) && typeof t.Reflect < "u" && !(q in t.Reflect) && typeof t.Reflect.defineMetadata == "function" && (s = Ct(t.Reflect));
        var o, a, _, D = new B(), H = {
          registerProvider: Q,
          getProvider: y,
          setProvider: w
        };
        return H;
        function Q(b) {
          if (!Object.isExtensible(H)) throw new Error("Cannot add provider to a frozen registry.");
          switch (true) {
            case s === b:
              break;
            case A(o):
              o = b;
              break;
            case o === b:
              break;
            case A(a):
              a = b;
              break;
            case a === b:
              break;
            default:
              _ === void 0 && (_ = new G()), _.add(b);
              break;
          }
        }
        function T(b, L) {
          if (!A(o)) {
            if (o.isProviderFor(b, L)) return o;
            if (!A(a)) {
              if (a.isProviderFor(b, L)) return o;
              if (!A(_)) for (var U = et(_); ; ) {
                var X = nt(U);
                if (!X) return;
                var fe = tt(X);
                if (fe.isProviderFor(b, L)) return rt(U), fe;
              }
            }
          }
          if (!A(s) && s.isProviderFor(b, L)) return s;
        }
        function y(b, L) {
          var U = D.get(b), X;
          return A(U) || (X = U.get(L)), A(X) && (X = T(b, L), A(X) || (A(U) && (U = new g(), D.set(b, U)), U.set(L, X))), X;
        }
        function M(b) {
          if (A(b)) throw new TypeError();
          return o === b || a === b || !A(_) && _.has(b);
        }
        function w(b, L, U) {
          if (!M(U)) throw new Error("Metadata provider not registered.");
          var X = y(b, L);
          if (X !== U) {
            if (!A(X)) return false;
            var fe = D.get(b);
            A(fe) && (fe = new g(), D.set(b, fe)), fe.set(L, U);
          }
          return true;
        }
      }
      function wt() {
        var s;
        return !A(q) && J(t.Reflect) && Object.isExtensible(t.Reflect) && (s = t.Reflect[q]), A(s) && (s = Et()), !A(q) && J(t.Reflect) && Object.isExtensible(t.Reflect) && Object.defineProperty(t.Reflect, q, {
          enumerable: false,
          configurable: false,
          writable: false,
          value: s
        }), s;
      }
      function bt(s) {
        var o = new B(), a = {
          isProviderFor: function(M, w) {
            var b = o.get(M);
            return A(b) ? false : b.has(w);
          },
          OrdinaryDefineOwnMetadata: Q,
          OrdinaryHasOwnMetadata: D,
          OrdinaryGetOwnMetadata: H,
          OrdinaryOwnMetadataKeys: T,
          OrdinaryDeleteMetadata: y
        };
        return m.registerProvider(a), a;
        function _(M, w, b) {
          var L = o.get(M), U = false;
          if (A(L)) {
            if (!b) return;
            L = new g(), o.set(M, L), U = true;
          }
          var X = L.get(w);
          if (A(X)) {
            if (!b) return;
            if (X = new g(), L.set(w, X), !s.setProvider(M, w, a)) throw L.delete(w), U && o.delete(M), new Error("Wrong provider for target.");
          }
          return X;
        }
        function D(M, w, b) {
          var L = _(w, b, false);
          return A(L) ? false : f(L.has(M));
        }
        function H(M, w, b) {
          var L = _(w, b, false);
          if (!A(L)) return L.get(M);
        }
        function Q(M, w, b, L) {
          var U = _(b, L, true);
          U.set(M, w);
        }
        function T(M, w) {
          var b = [], L = _(M, w, false);
          if (A(L)) return b;
          for (var U = L.keys(), X = et(U), fe = 0; ; ) {
            var it = nt(X);
            if (!it) return b.length = fe, b;
            var It = tt(it);
            try {
              b[fe] = It;
            } catch (Rt) {
              try {
                rt(X);
              } finally {
                throw Rt;
              }
            }
            fe++;
          }
        }
        function y(M, w, b) {
          var L = _(w, b, false);
          if (A(L) || !L.delete(M)) return false;
          if (L.size === 0) {
            var U = o.get(w);
            A(U) || (U.delete(b), U.size === 0 && o.delete(U));
          }
          return true;
        }
      }
      function Ct(s) {
        var o = s.defineMetadata, a = s.hasOwnMetadata, _ = s.getOwnMetadata, D = s.getOwnMetadataKeys, H = s.deleteMetadata, Q = new B(), T = {
          isProviderFor: function(y, M) {
            var w = Q.get(y);
            return !A(w) && w.has(M) ? true : D(y, M).length ? (A(w) && (w = new G(), Q.set(y, w)), w.add(M), true) : false;
          },
          OrdinaryDefineOwnMetadata: o,
          OrdinaryHasOwnMetadata: a,
          OrdinaryGetOwnMetadata: _,
          OrdinaryOwnMetadataKeys: D,
          OrdinaryDeleteMetadata: H
        };
        return T;
      }
      function Pe(s, o, a) {
        var _ = m.getProvider(s, o);
        if (!A(_)) return _;
        if (a) {
          if (m.setProvider(s, o, F)) return F;
          throw new Error("Illegal state.");
        }
      }
      function Ot() {
        var s = {}, o = [], a = function() {
          function T(y, M, w) {
            this._index = 0, this._keys = y, this._values = M, this._selector = w;
          }
          return T.prototype["@@iterator"] = function() {
            return this;
          }, T.prototype[c] = function() {
            return this;
          }, T.prototype.next = function() {
            var y = this._index;
            if (y >= 0 && y < this._keys.length) {
              var M = this._selector(this._keys[y], this._values[y]);
              return y + 1 >= this._keys.length ? (this._index = -1, this._keys = o, this._values = o) : this._index++, {
                value: M,
                done: false
              };
            }
            return {
              value: void 0,
              done: true
            };
          }, T.prototype.throw = function(y) {
            throw this._index >= 0 && (this._index = -1, this._keys = o, this._values = o), y;
          }, T.prototype.return = function(y) {
            return this._index >= 0 && (this._index = -1, this._keys = o, this._values = o), {
              value: y,
              done: true
            };
          }, T;
        }(), _ = function() {
          function T() {
            this._keys = [], this._values = [], this._cacheKey = s, this._cacheIndex = -2;
          }
          return Object.defineProperty(T.prototype, "size", {
            get: function() {
              return this._keys.length;
            },
            enumerable: true,
            configurable: true
          }), T.prototype.has = function(y) {
            return this._find(y, false) >= 0;
          }, T.prototype.get = function(y) {
            var M = this._find(y, false);
            return M >= 0 ? this._values[M] : void 0;
          }, T.prototype.set = function(y, M) {
            var w = this._find(y, true);
            return this._values[w] = M, this;
          }, T.prototype.delete = function(y) {
            var M = this._find(y, false);
            if (M >= 0) {
              for (var w = this._keys.length, b = M + 1; b < w; b++) this._keys[b - 1] = this._keys[b], this._values[b - 1] = this._values[b];
              return this._keys.length--, this._values.length--, Ye(y, this._cacheKey) && (this._cacheKey = s, this._cacheIndex = -2), true;
            }
            return false;
          }, T.prototype.clear = function() {
            this._keys.length = 0, this._values.length = 0, this._cacheKey = s, this._cacheIndex = -2;
          }, T.prototype.keys = function() {
            return new a(this._keys, this._values, D);
          }, T.prototype.values = function() {
            return new a(this._keys, this._values, H);
          }, T.prototype.entries = function() {
            return new a(this._keys, this._values, Q);
          }, T.prototype["@@iterator"] = function() {
            return this.entries();
          }, T.prototype[c] = function() {
            return this.entries();
          }, T.prototype._find = function(y, M) {
            if (!Ye(this._cacheKey, y)) {
              this._cacheIndex = -1;
              for (var w = 0; w < this._keys.length; w++) if (Ye(this._keys[w], y)) {
                this._cacheIndex = w;
                break;
              }
            }
            return this._cacheIndex < 0 && M && (this._cacheIndex = this._keys.length, this._keys.push(y), this._values.push(void 0)), this._cacheIndex;
          }, T;
        }();
        return _;
        function D(T, y) {
          return T;
        }
        function H(T, y) {
          return y;
        }
        function Q(T, y) {
          return [
            T,
            y
          ];
        }
      }
      function At() {
        var s = function() {
          function o() {
            this._map = new g();
          }
          return Object.defineProperty(o.prototype, "size", {
            get: function() {
              return this._map.size;
            },
            enumerable: true,
            configurable: true
          }), o.prototype.has = function(a) {
            return this._map.has(a);
          }, o.prototype.add = function(a) {
            return this._map.set(a, a), this;
          }, o.prototype.delete = function(a) {
            return this._map.delete(a);
          }, o.prototype.clear = function() {
            this._map.clear();
          }, o.prototype.keys = function() {
            return this._map.keys();
          }, o.prototype.values = function() {
            return this._map.keys();
          }, o.prototype.entries = function() {
            return this._map.entries();
          }, o.prototype["@@iterator"] = function() {
            return this.keys();
          }, o.prototype[c] = function() {
            return this.keys();
          }, o;
        }();
        return s;
      }
      function Dt() {
        var s = 16, o = u.create(), a = _();
        return function() {
          function y() {
            this._key = _();
          }
          return y.prototype.has = function(M) {
            var w = D(M, false);
            return w !== void 0 ? u.has(w, this._key) : false;
          }, y.prototype.get = function(M) {
            var w = D(M, false);
            return w !== void 0 ? u.get(w, this._key) : void 0;
          }, y.prototype.set = function(M, w) {
            var b = D(M, true);
            return b[this._key] = w, this;
          }, y.prototype.delete = function(M) {
            var w = D(M, false);
            return w !== void 0 ? delete w[this._key] : false;
          }, y.prototype.clear = function() {
            this._key = _();
          }, y;
        }();
        function _() {
          var y;
          do
            y = "@@WeakMap@@" + T();
          while (u.has(o, y));
          return o[y] = true, y;
        }
        function D(y, M) {
          if (!r.call(y, a)) {
            if (!M) return;
            Object.defineProperty(y, a, {
              value: u.create()
            });
          }
          return y[a];
        }
        function H(y, M) {
          for (var w = 0; w < M; ++w) y[w] = Math.random() * 255 | 0;
          return y;
        }
        function Q(y) {
          if (typeof Uint8Array == "function") {
            var M = new Uint8Array(y);
            return typeof crypto < "u" ? crypto.getRandomValues(M) : typeof msCrypto < "u" ? msCrypto.getRandomValues(M) : H(M, y), M;
          }
          return H(new Array(y), y);
        }
        function T() {
          var y = Q(s);
          y[6] = y[6] & 79 | 64, y[8] = y[8] & 191 | 128;
          for (var M = "", w = 0; w < s; ++w) {
            var b = y[w];
            (w === 4 || w === 6 || w === 8) && (M += "-"), b < 16 && (M += "0"), M += b.toString(16).toLowerCase();
          }
          return M;
        }
      }
      function Xe(s) {
        return s.__ = void 0, delete s.__, s;
      }
    });
  })(ot || (ot = {}));
  (function(n) {
    var e = O && O.__decorate || function(S, f, C, E) {
      var x = arguments.length, N = x < 3 ? f : E === null ? E = Object.getOwnPropertyDescriptor(f, C) : E, Z;
      if (typeof Reflect == "object" && typeof Reflect.decorate == "function") N = Reflect.decorate(S, f, C, E);
      else for (var ie = S.length - 1; ie >= 0; ie--) (Z = S[ie]) && (N = (x < 3 ? Z(N) : x > 3 ? Z(f, C, N) : Z(f, C)) || N);
      return x > 3 && N && Object.defineProperty(f, C, N), N;
    }, t = O && O.__metadata || function(S, f) {
      if (typeof Reflect == "object" && typeof Reflect.metadata == "function") return Reflect.metadata(S, f);
    };
    Object.defineProperty(n, "__esModule", {
      value: true
    }), n.RawReading = n.RawUnsubscribeCmd = n.RawSubscribeCmd = n.RawWriteCmd = n.RawReadCmd = n.SensorReading = n.SensorReadCmd = n.LinearCmd = n.VectorSubcommand = n.RotateCmd = n.RotateSubcommand = n.ScalarCmd = n.ScalarSubcommand = n.GenericMessageSubcommand = n.StopAllDevices = n.StopDeviceCmd = n.ServerInfo = n.RequestServerInfo = n.ScanningFinished = n.StopScanning = n.StartScanning = n.RequestDeviceList = n.DeviceRemoved = n.DeviceAdded = n.DeviceList = n.DeviceInfo = n.Error = n.ErrorClass = n.Ping = n.Ok = n.ButtplugSystemMessage = n.ButtplugDeviceMessage = n.ButtplugMessage = n.SensorDeviceMessageAttributes = n.RawDeviceMessageAttributes = n.GenericDeviceMessageAttributes = n.SensorType = n.ActuatorType = n.MessageAttributes = n.MESSAGE_SPEC_VERSION = n.MAX_ID = n.DEFAULT_MESSAGE_ID = n.SYSTEM_MESSAGE_ID = void 0;
    const r = pt;
    n.SYSTEM_MESSAGE_ID = 0, n.DEFAULT_MESSAGE_ID = 1, n.MAX_ID = 4294967295, n.MESSAGE_SPEC_VERSION = 3;
    class i {
      constructor(f) {
        Object.assign(this, f);
      }
      update() {
        var f, C, E, x, N;
        (f = this.ScalarCmd) === null || f === void 0 || f.forEach((Z, ie) => Z.Index = ie), (C = this.RotateCmd) === null || C === void 0 || C.forEach((Z, ie) => Z.Index = ie), (E = this.LinearCmd) === null || E === void 0 || E.forEach((Z, ie) => Z.Index = ie), (x = this.SensorReadCmd) === null || x === void 0 || x.forEach((Z, ie) => Z.Index = ie), (N = this.SensorSubscribeCmd) === null || N === void 0 || N.forEach((Z, ie) => Z.Index = ie);
      }
    }
    n.MessageAttributes = i;
    var d;
    (function(S) {
      S.Unknown = "Unknown", S.Vibrate = "Vibrate", S.Rotate = "Rotate", S.Oscillate = "Oscillate", S.Constrict = "Constrict", S.Inflate = "Inflate", S.Position = "Position";
    })(d || (n.ActuatorType = d = {}));
    var c;
    (function(S) {
      S.Unknown = "Unknown", S.Battery = "Battery", S.RSSI = "RSSI", S.Button = "Button", S.Pressure = "Pressure";
    })(c || (n.SensorType = c = {}));
    class h {
      constructor(f) {
        this.Index = 0, Object.assign(this, f);
      }
    }
    n.GenericDeviceMessageAttributes = h;
    class l {
      constructor(f) {
        this.Endpoints = f;
      }
    }
    n.RawDeviceMessageAttributes = l;
    class v {
      constructor(f) {
        this.Index = 0, Object.assign(this, f);
      }
    }
    n.SensorDeviceMessageAttributes = v;
    class u {
      constructor(f) {
        this.Id = f;
      }
      get Type() {
        return this.constructor;
      }
      toJSON() {
        return JSON.stringify(this.toProtocolFormat());
      }
      toProtocolFormat() {
        const f = {};
        return f[this.constructor.Name] = (0, r.instanceToPlain)(this), f;
      }
      update() {
      }
    }
    n.ButtplugMessage = u;
    class p extends u {
      constructor(f, C) {
        super(C), this.DeviceIndex = f, this.Id = C;
      }
    }
    n.ButtplugDeviceMessage = p;
    class g extends u {
      constructor(f = n.SYSTEM_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.ButtplugSystemMessage = g;
    class G extends g {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.Ok = G, G.Name = "Ok";
    class B extends u {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.Ping = B, B.Name = "Ping";
    var q;
    (function(S) {
      S[S.ERROR_UNKNOWN = 0] = "ERROR_UNKNOWN", S[S.ERROR_INIT = 1] = "ERROR_INIT", S[S.ERROR_PING = 2] = "ERROR_PING", S[S.ERROR_MSG = 3] = "ERROR_MSG", S[S.ERROR_DEVICE = 4] = "ERROR_DEVICE";
    })(q || (n.ErrorClass = q = {}));
    class m extends u {
      constructor(f, C = q.ERROR_UNKNOWN, E = n.DEFAULT_MESSAGE_ID) {
        super(E), this.ErrorMessage = f, this.ErrorCode = C, this.Id = E;
      }
      get Schemversion() {
        return 0;
      }
    }
    n.Error = m, m.Name = "Error";
    class F {
      constructor(f) {
        Object.assign(this, f);
      }
    }
    n.DeviceInfo = F, e([
      (0, r.Type)(() => i),
      t("design:type", i)
    ], F.prototype, "DeviceMessages", void 0);
    class $ extends u {
      constructor(f, C = n.DEFAULT_MESSAGE_ID) {
        super(C), this.Devices = f, this.Id = C;
      }
      update() {
        for (const f of this.Devices) f.DeviceMessages.update();
      }
    }
    n.DeviceList = $, $.Name = "DeviceList", e([
      (0, r.Type)(() => F),
      t("design:type", Array)
    ], $.prototype, "Devices", void 0);
    class I extends g {
      constructor(f) {
        super(), Object.assign(this, f);
      }
      update() {
        this.DeviceMessages.update();
      }
    }
    n.DeviceAdded = I, I.Name = "DeviceAdded", e([
      (0, r.Type)(() => i),
      t("design:type", i)
    ], I.prototype, "DeviceMessages", void 0);
    class te extends g {
      constructor(f) {
        super(), this.DeviceIndex = f;
      }
    }
    n.DeviceRemoved = te, te.Name = "DeviceRemoved";
    class P extends u {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.RequestDeviceList = P, P.Name = "RequestDeviceList";
    class Y extends u {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.StartScanning = Y, Y.Name = "StartScanning";
    class ae extends u {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.StopScanning = ae, ae.Name = "StopScanning";
    class W extends g {
      constructor() {
        super();
      }
    }
    n.ScanningFinished = W, W.Name = "ScanningFinished";
    class Ce extends u {
      constructor(f, C = 0, E = n.DEFAULT_MESSAGE_ID) {
        super(E), this.ClientName = f, this.MessageVersion = C, this.Id = E;
      }
    }
    n.RequestServerInfo = Ce, Ce.Name = "RequestServerInfo";
    class Se extends g {
      constructor(f, C, E, x = n.DEFAULT_MESSAGE_ID) {
        super(), this.MessageVersion = f, this.MaxPingTime = C, this.ServerName = E, this.Id = x;
      }
    }
    n.ServerInfo = Se, Se.Name = "ServerInfo";
    class Me extends p {
      constructor(f = -1, C = n.DEFAULT_MESSAGE_ID) {
        super(f, C), this.DeviceIndex = f, this.Id = C;
      }
    }
    n.StopDeviceCmd = Me, Me.Name = "StopDeviceCmd";
    class Ee extends u {
      constructor(f = n.DEFAULT_MESSAGE_ID) {
        super(f), this.Id = f;
      }
    }
    n.StopAllDevices = Ee, Ee.Name = "StopAllDevices";
    class he {
      constructor(f) {
        this.Index = f;
      }
    }
    n.GenericMessageSubcommand = he;
    class we extends he {
      constructor(f, C, E) {
        super(f), this.Scalar = C, this.ActuatorType = E;
      }
    }
    n.ScalarSubcommand = we;
    class ce extends p {
      constructor(f, C = -1, E = n.DEFAULT_MESSAGE_ID) {
        super(C, E), this.Scalars = f, this.DeviceIndex = C, this.Id = E;
      }
    }
    n.ScalarCmd = ce, ce.Name = "ScalarCmd";
    class k extends he {
      constructor(f, C, E) {
        super(f), this.Speed = C, this.Clockwise = E;
      }
    }
    n.RotateSubcommand = k;
    class ne extends p {
      static Create(f, C) {
        const E = new Array();
        let x = 0;
        for (const [N, Z] of C) E.push(new k(x, N, Z)), ++x;
        return new ne(E, f);
      }
      constructor(f, C = -1, E = n.DEFAULT_MESSAGE_ID) {
        super(C, E), this.Rotations = f, this.DeviceIndex = C, this.Id = E;
      }
    }
    n.RotateCmd = ne, ne.Name = "RotateCmd";
    class Re extends he {
      constructor(f, C, E) {
        super(f), this.Position = C, this.Duration = E;
      }
    }
    n.VectorSubcommand = Re;
    class be extends p {
      static Create(f, C) {
        const E = new Array();
        let x = 0;
        for (const N of C) E.push(new Re(x, N[0], N[1])), ++x;
        return new be(E, f);
      }
      constructor(f, C = -1, E = n.DEFAULT_MESSAGE_ID) {
        super(C, E), this.Vectors = f, this.DeviceIndex = C, this.Id = E;
      }
    }
    n.LinearCmd = be, be.Name = "LinearCmd";
    class Te extends p {
      constructor(f, C, E, x = n.DEFAULT_MESSAGE_ID) {
        super(f, x), this.DeviceIndex = f, this.SensorIndex = C, this.SensorType = E, this.Id = x;
      }
    }
    n.SensorReadCmd = Te, Te.Name = "SensorReadCmd";
    class Le extends p {
      constructor(f, C, E, x, N = n.DEFAULT_MESSAGE_ID) {
        super(f, N), this.DeviceIndex = f, this.SensorIndex = C, this.SensorType = E, this.Data = x, this.Id = N;
      }
    }
    n.SensorReading = Le, Le.Name = "SensorReading";
    class A extends p {
      constructor(f, C, E, x, N = n.DEFAULT_MESSAGE_ID) {
        super(f, N), this.DeviceIndex = f, this.Endpoint = C, this.ExpectedLength = E, this.Timeout = x, this.Id = N;
      }
    }
    n.RawReadCmd = A, A.Name = "RawReadCmd";
    class pe extends p {
      constructor(f, C, E, x, N = n.DEFAULT_MESSAGE_ID) {
        super(f, N), this.DeviceIndex = f, this.Endpoint = C, this.Data = E, this.WriteWithResponse = x, this.Id = N;
      }
    }
    n.RawWriteCmd = pe, pe.Name = "RawWriteCmd";
    class $e extends p {
      constructor(f, C, E = n.DEFAULT_MESSAGE_ID) {
        super(f, E), this.DeviceIndex = f, this.Endpoint = C, this.Id = E;
      }
    }
    n.RawSubscribeCmd = $e, $e.Name = "RawSubscribeCmd";
    class J extends p {
      constructor(f, C, E = n.DEFAULT_MESSAGE_ID) {
        super(f, E), this.DeviceIndex = f, this.Endpoint = C, this.Id = E;
      }
    }
    n.RawUnsubscribeCmd = J, J.Name = "RawUnsubscribeCmd";
    class Ge extends p {
      constructor(f, C, E, x = n.DEFAULT_MESSAGE_ID) {
        super(f, x), this.DeviceIndex = f, this.Endpoint = C, this.Data = E, this.Id = x;
      }
    }
    n.RawReading = Ge, Ge.Name = "RawReading";
  })(me);
  var ee = {};
  var sn = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), on = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), an = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && sn(e, n, t);
    return on(e, n), e;
  };
  Object.defineProperty(ee, "__esModule", {
    value: true
  });
  ee.ButtplugUnknownError = ee.ButtplugPingError = ee.ButtplugMessageError = ee.ButtplugDeviceError = ee.ButtplugInitError = ee.ButtplugError = void 0;
  const K = an(me);
  class Ie extends Error {
    get ErrorClass() {
      return this.errorClass;
    }
    get InnerError() {
      return this.innerError;
    }
    get Id() {
      return this.messageId;
    }
    get ErrorMessage() {
      return new K.Error(this.message, this.ErrorClass, this.Id);
    }
    static LogAndError(e, t, r, i = K.SYSTEM_MESSAGE_ID) {
      return t.Error(r), new e(r, i);
    }
    static FromError(e) {
      switch (e.ErrorCode) {
        case K.ErrorClass.ERROR_DEVICE:
          return new vt(e.ErrorMessage, e.Id);
        case K.ErrorClass.ERROR_INIT:
          return new gt(e.ErrorMessage, e.Id);
        case K.ErrorClass.ERROR_UNKNOWN:
          return new mt(e.ErrorMessage, e.Id);
        case K.ErrorClass.ERROR_PING:
          return new yt(e.ErrorMessage, e.Id);
        case K.ErrorClass.ERROR_MSG:
          return new _t(e.ErrorMessage, e.Id);
        default:
          throw new Error(`Message type ${e.ErrorCode} not handled`);
      }
    }
    constructor(e, t, r = K.SYSTEM_MESSAGE_ID, i) {
      super(e), this.errorClass = K.ErrorClass.ERROR_UNKNOWN, this.errorClass = t, this.innerError = i, this.messageId = r;
    }
  }
  ee.ButtplugError = Ie;
  class gt extends Ie {
    constructor(e, t = K.SYSTEM_MESSAGE_ID) {
      super(e, K.ErrorClass.ERROR_INIT, t);
    }
  }
  ee.ButtplugInitError = gt;
  class vt extends Ie {
    constructor(e, t = K.SYSTEM_MESSAGE_ID) {
      super(e, K.ErrorClass.ERROR_DEVICE, t);
    }
  }
  ee.ButtplugDeviceError = vt;
  class _t extends Ie {
    constructor(e, t = K.SYSTEM_MESSAGE_ID) {
      super(e, K.ErrorClass.ERROR_MSG, t);
    }
  }
  ee.ButtplugMessageError = _t;
  class yt extends Ie {
    constructor(e, t = K.SYSTEM_MESSAGE_ID) {
      super(e, K.ErrorClass.ERROR_PING, t);
    }
  }
  ee.ButtplugPingError = yt;
  class mt extends Ie {
    constructor(e, t = K.SYSTEM_MESSAGE_ID) {
      super(e, K.ErrorClass.ERROR_UNKNOWN, t);
    }
  }
  ee.ButtplugUnknownError = mt;
  var _e = {};
  var un = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), cn = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), fn = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && un(e, n, t);
    return cn(e, n), e;
  };
  Object.defineProperty(_e, "__esModule", {
    value: true
  });
  _e.fromJSON = _e.getMessageClassFromMessage = void 0;
  const dn = pt, ln = fn(me);
  function St(n) {
    for (const e of Object.values(ln)) if (typeof e == "function" && "Name" in e && e.Name === n) return e;
    return null;
  }
  function hn(n) {
    return St(Object.getPrototypeOf(n).constructor.Name);
  }
  _e.getMessageClassFromMessage = hn;
  function pn(n) {
    const e = JSON.parse(n), t = [];
    for (const r of Array.from(e)) {
      const i = Object.getOwnPropertyNames(r)[0], d = St(i);
      if (d) {
        const c = (0, dn.plainToInstance)(d, r[i]);
        c.update(), t.push(c);
      }
    }
    return t;
  }
  _e.fromJSON = pn;
  var gn = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), vn = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), _n = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && gn(e, n, t);
    return vn(e, n), e;
  }, re = O && O.__awaiter || function(n, e, t, r) {
    function i(d) {
      return d instanceof t ? d : new t(function(c) {
        c(d);
      });
    }
    return new (t || (t = Promise))(function(d, c) {
      function h(u) {
        try {
          v(r.next(u));
        } catch (p) {
          c(p);
        }
      }
      function l(u) {
        try {
          v(r.throw(u));
        } catch (p) {
          c(p);
        }
      }
      function v(u) {
        u.done ? d(u.value) : i(u.value).then(h, l);
      }
      v((r = r.apply(n, e || [])).next());
    });
  };
  Object.defineProperty(Be, "__esModule", {
    value: true
  });
  Be.ButtplugClientDevice = void 0;
  const j = _n(me), z = ee, yn = ze, Ze = _e;
  class Ke extends yn.EventEmitter {
    get name() {
      return this._deviceInfo.DeviceName;
    }
    get displayName() {
      return this._deviceInfo.DeviceDisplayName;
    }
    get index() {
      return this._deviceInfo.DeviceIndex;
    }
    get messageTimingGap() {
      return this._deviceInfo.DeviceMessageTimingGap;
    }
    get messageAttributes() {
      return this._deviceInfo.DeviceMessages;
    }
    static fromMsg(e, t) {
      return new Ke(e, t);
    }
    constructor(e, t) {
      super(), this._deviceInfo = e, this._sendClosure = t, this.allowedMsgs = /* @__PURE__ */ new Map(), e.DeviceMessages.update();
    }
    send(e) {
      return re(this, void 0, void 0, function* () {
        return yield this._sendClosure(this, e);
      });
    }
    sendExpectOk(e) {
      return re(this, void 0, void 0, function* () {
        const t = yield this.send(e);
        switch ((0, Ze.getMessageClassFromMessage)(t)) {
          case j.Ok:
            return;
          case j.Error:
            throw z.ButtplugError.FromError(t);
          default:
            throw new z.ButtplugMessageError(`Message type ${t.constructor} not handled by SendMsgExpectOk`);
        }
      });
    }
    scalar(e) {
      return re(this, void 0, void 0, function* () {
        Array.isArray(e) ? yield this.sendExpectOk(new j.ScalarCmd(e, this.index)) : yield this.sendExpectOk(new j.ScalarCmd([
          e
        ], this.index));
      });
    }
    scalarCommandBuilder(e, t) {
      var r;
      return re(this, void 0, void 0, function* () {
        const i = (r = this.messageAttributes.ScalarCmd) === null || r === void 0 ? void 0 : r.filter((c) => c.ActuatorType === t);
        if (!i || i.length === 0) throw new z.ButtplugDeviceError(`Device ${this.name} has no ${t} capabilities`);
        const d = [];
        if (typeof e == "number") i.forEach((c) => d.push(new j.ScalarSubcommand(c.Index, e, t)));
        else if (Array.isArray(e)) {
          if (e.length > i.length) throw new z.ButtplugDeviceError(`${e.length} commands send to a device with ${i.length} vibrators`);
          i.forEach((c, h) => {
            d.push(new j.ScalarSubcommand(c.Index, e[h], t));
          });
        } else throw new z.ButtplugDeviceError(`${t} can only take numbers or arrays of numbers.`);
        yield this.scalar(d);
      });
    }
    get vibrateAttributes() {
      var e, t;
      return (t = (e = this.messageAttributes.ScalarCmd) === null || e === void 0 ? void 0 : e.filter((r) => r.ActuatorType === j.ActuatorType.Vibrate)) !== null && t !== void 0 ? t : [];
    }
    vibrate(e) {
      return re(this, void 0, void 0, function* () {
        yield this.scalarCommandBuilder(e, j.ActuatorType.Vibrate);
      });
    }
    get oscillateAttributes() {
      var e, t;
      return (t = (e = this.messageAttributes.ScalarCmd) === null || e === void 0 ? void 0 : e.filter((r) => r.ActuatorType === j.ActuatorType.Oscillate)) !== null && t !== void 0 ? t : [];
    }
    oscillate(e) {
      return re(this, void 0, void 0, function* () {
        yield this.scalarCommandBuilder(e, j.ActuatorType.Oscillate);
      });
    }
    get rotateAttributes() {
      var e;
      return (e = this.messageAttributes.RotateCmd) !== null && e !== void 0 ? e : [];
    }
    rotate(e, t) {
      return re(this, void 0, void 0, function* () {
        const r = this.messageAttributes.RotateCmd;
        if (!r || r.length === 0) throw new z.ButtplugDeviceError(`Device ${this.name} has no Rotate capabilities`);
        let i;
        if (typeof e == "number") i = j.RotateCmd.Create(this.index, new Array(r.length).fill([
          e,
          t
        ]));
        else if (Array.isArray(e)) i = j.RotateCmd.Create(this.index, e);
        else throw new z.ButtplugDeviceError("SendRotateCmd can only take a number and boolean, or an array of number/boolean tuples");
        yield this.sendExpectOk(i);
      });
    }
    get linearAttributes() {
      var e;
      return (e = this.messageAttributes.LinearCmd) !== null && e !== void 0 ? e : [];
    }
    linear(e, t) {
      return re(this, void 0, void 0, function* () {
        const r = this.messageAttributes.LinearCmd;
        if (!r || r.length === 0) throw new z.ButtplugDeviceError(`Device ${this.name} has no Linear capabilities`);
        let i;
        if (typeof e == "number") i = j.LinearCmd.Create(this.index, new Array(r.length).fill([
          e,
          t
        ]));
        else if (Array.isArray(e)) i = j.LinearCmd.Create(this.index, e);
        else throw new z.ButtplugDeviceError("SendLinearCmd can only take a number and number, or an array of number/number tuples");
        yield this.sendExpectOk(i);
      });
    }
    sensorRead(e, t) {
      return re(this, void 0, void 0, function* () {
        const r = yield this.send(new j.SensorReadCmd(this.index, e, t));
        switch ((0, Ze.getMessageClassFromMessage)(r)) {
          case j.SensorReading:
            return r.Data;
          case j.Error:
            throw z.ButtplugError.FromError(r);
          default:
            throw new z.ButtplugMessageError(`Message type ${r.constructor} not handled by sensorRead`);
        }
      });
    }
    get hasBattery() {
      var e;
      const t = (e = this.messageAttributes.SensorReadCmd) === null || e === void 0 ? void 0 : e.filter((r) => r.SensorType === j.SensorType.Battery);
      return t !== void 0 && t.length > 0;
    }
    battery() {
      var e;
      return re(this, void 0, void 0, function* () {
        if (!this.hasBattery) throw new z.ButtplugDeviceError(`Device ${this.name} has no Battery capabilities`);
        const t = (e = this.messageAttributes.SensorReadCmd) === null || e === void 0 ? void 0 : e.filter((i) => i.SensorType === j.SensorType.Battery);
        return (yield this.sensorRead(t[0].Index, j.SensorType.Battery))[0] / 100;
      });
    }
    get hasRssi() {
      var e;
      const t = (e = this.messageAttributes.SensorReadCmd) === null || e === void 0 ? void 0 : e.filter((r) => r.SensorType === j.SensorType.RSSI);
      return t !== void 0 && t.length === 0;
    }
    rssi() {
      var e;
      return re(this, void 0, void 0, function* () {
        if (!this.hasRssi) throw new z.ButtplugDeviceError(`Device ${this.name} has no RSSI capabilities`);
        const t = (e = this.messageAttributes.SensorReadCmd) === null || e === void 0 ? void 0 : e.filter((i) => i.SensorType === j.SensorType.RSSI);
        return (yield this.sensorRead(t[0].Index, j.SensorType.RSSI))[0];
      });
    }
    rawRead(e, t, r) {
      return re(this, void 0, void 0, function* () {
        if (!this.messageAttributes.RawReadCmd) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw read capabilities`);
        if (this.messageAttributes.RawReadCmd.Endpoints.indexOf(e) === -1) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw readable endpoint ${e}`);
        const i = yield this.send(new j.RawReadCmd(this.index, e, t, r));
        switch ((0, Ze.getMessageClassFromMessage)(i)) {
          case j.RawReading:
            return new Uint8Array(i.Data);
          case j.Error:
            throw z.ButtplugError.FromError(i);
          default:
            throw new z.ButtplugMessageError(`Message type ${i.constructor} not handled by rawRead`);
        }
      });
    }
    rawWrite(e, t, r) {
      return re(this, void 0, void 0, function* () {
        if (!this.messageAttributes.RawWriteCmd) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw write capabilities`);
        if (this.messageAttributes.RawWriteCmd.Endpoints.indexOf(e) === -1) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw writable endpoint ${e}`);
        yield this.sendExpectOk(new j.RawWriteCmd(this.index, e, t, r));
      });
    }
    rawSubscribe(e) {
      return re(this, void 0, void 0, function* () {
        if (!this.messageAttributes.RawSubscribeCmd) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw subscribe capabilities`);
        if (this.messageAttributes.RawSubscribeCmd.Endpoints.indexOf(e) === -1) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw subscribable endpoint ${e}`);
        yield this.sendExpectOk(new j.RawSubscribeCmd(this.index, e));
      });
    }
    rawUnsubscribe(e) {
      return re(this, void 0, void 0, function* () {
        if (!this.messageAttributes.RawSubscribeCmd) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw unsubscribe capabilities`);
        if (this.messageAttributes.RawSubscribeCmd.Endpoints.indexOf(e) === -1) throw new z.ButtplugDeviceError(`Device ${this.name} has no raw unsubscribable endpoint ${e}`);
        yield this.sendExpectOk(new j.RawUnsubscribeCmd(this.index, e));
      });
    }
    stop() {
      return re(this, void 0, void 0, function* () {
        yield this.sendExpectOk(new j.StopDeviceCmd(this.index));
      });
    }
    emitDisconnected() {
      this.emit("deviceremoved");
    }
  }
  Be.ButtplugClientDevice = Ke;
  var Ne = {};
  var mn = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), Sn = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), Mn = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && mn(e, n, t);
    return Sn(e, n), e;
  };
  Object.defineProperty(Ne, "__esModule", {
    value: true
  });
  Ne.ButtplugMessageSorter = void 0;
  const at = Mn(me), En = ee;
  class wn {
    constructor(e) {
      this._useCounter = e, this._counter = 1, this._waitingMsgs = /* @__PURE__ */ new Map();
    }
    PrepareOutgoingMessage(e) {
      this._useCounter && (e.Id = this._counter, this._counter += 1);
      let t, r;
      const i = new Promise((d, c) => {
        t = d, r = c;
      });
      return this._waitingMsgs.set(e.Id, [
        t,
        r
      ]), i;
    }
    ParseIncomingMessages(e) {
      const t = [];
      for (const r of e) if (r.Id !== at.SYSTEM_MESSAGE_ID && this._waitingMsgs.has(r.Id)) {
        const [i, d] = this._waitingMsgs.get(r.Id);
        if (r.Type === at.Error) {
          d(En.ButtplugError.FromError(r));
          continue;
        }
        i(r);
        continue;
      } else t.push(r);
      return t;
    }
  }
  Ne.ButtplugMessageSorter = wn;
  var je = {};
  var bn = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), Cn = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), On = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && bn(e, n, t);
    return Cn(e, n), e;
  };
  Object.defineProperty(je, "__esModule", {
    value: true
  });
  je.ButtplugClientConnectorException = void 0;
  const An = ee, Dn = On(me);
  class In extends An.ButtplugError {
    constructor(e) {
      super(e, Dn.ErrorClass.ERROR_UNKNOWN);
    }
  }
  je.ButtplugClientConnectorException = In;
  var Rn = O && O.__createBinding || (Object.create ? function(n, e, t, r) {
    r === void 0 && (r = t);
    var i = Object.getOwnPropertyDescriptor(e, t);
    (!i || ("get" in i ? !e.__esModule : i.writable || i.configurable)) && (i = {
      enumerable: true,
      get: function() {
        return e[t];
      }
    }), Object.defineProperty(n, r, i);
  } : function(n, e, t, r) {
    r === void 0 && (r = t), n[r] = e[t];
  }), Tn = O && O.__setModuleDefault || (Object.create ? function(n, e) {
    Object.defineProperty(n, "default", {
      enumerable: true,
      value: e
    });
  } : function(n, e) {
    n.default = e;
  }), Ln = O && O.__importStar || function(n) {
    if (n && n.__esModule) return n;
    var e = {};
    if (n != null) for (var t in n) t !== "default" && Object.prototype.hasOwnProperty.call(n, t) && Rn(e, n, t);
    return Tn(e, n), e;
  }, ue = O && O.__awaiter || function(n, e, t, r) {
    function i(d) {
      return d instanceof t ? d : new t(function(c) {
        c(d);
      });
    }
    return new (t || (t = Promise))(function(d, c) {
      function h(u) {
        try {
          v(r.next(u));
        } catch (p) {
          c(p);
        }
      }
      function l(u) {
        try {
          v(r.throw(u));
        } catch (p) {
          c(p);
        }
      }
      function v(u) {
        u.done ? d(u.value) : i(u.value).then(h, l);
      }
      v((r = r.apply(n, e || [])).next());
    });
  };
  Object.defineProperty(We, "__esModule", {
    value: true
  });
  We.ButtplugClient = void 0;
  const Pn = ve, Bn = ze, ut = Be, xn = Ne, se = Ln(me), ge = ee, Nn = je, ke = _e;
  class jn extends Bn.EventEmitter {
    constructor(e = "Generic Buttplug Client") {
      super(), this._pingTimer = null, this._connector = null, this._devices = /* @__PURE__ */ new Map(), this._logger = Pn.ButtplugLogger.Logger, this._isScanning = false, this._sorter = new xn.ButtplugMessageSorter(true), this.connect = (t) => ue(this, void 0, void 0, function* () {
        this._logger.Info(`ButtplugClient: Connecting using ${t.constructor.name}`), yield t.connect(), this._connector = t, this._connector.addListener("message", this.parseMessages), this._connector.addListener("disconnect", this.disconnectHandler), yield this.initializeConnection();
      }), this.disconnect = () => ue(this, void 0, void 0, function* () {
        this._logger.Debug("ButtplugClient: Disconnect called"), this.checkConnector(), yield this.shutdownConnection(), yield this._connector.disconnect();
      }), this.startScanning = () => ue(this, void 0, void 0, function* () {
        this._logger.Debug("ButtplugClient: StartScanning called"), this._isScanning = true, yield this.sendMsgExpectOk(new se.StartScanning());
      }), this.stopScanning = () => ue(this, void 0, void 0, function* () {
        this._logger.Debug("ButtplugClient: StopScanning called"), this._isScanning = false, yield this.sendMsgExpectOk(new se.StopScanning());
      }), this.stopAllDevices = () => ue(this, void 0, void 0, function* () {
        this._logger.Debug("ButtplugClient: StopAllDevices"), yield this.sendMsgExpectOk(new se.StopAllDevices());
      }), this.disconnectHandler = () => {
        this._logger.Info("ButtplugClient: Disconnect event receieved."), this.emit("disconnect");
      }, this.parseMessages = (t) => {
        const r = this._sorter.ParseIncomingMessages(t);
        for (const i of r) switch ((0, ke.getMessageClassFromMessage)(i)) {
          case se.DeviceAdded: {
            const d = i, c = ut.ButtplugClientDevice.fromMsg(d, this.sendDeviceMessageClosure);
            this._devices.set(d.DeviceIndex, c), this.emit("deviceadded", c);
            break;
          }
          case se.DeviceRemoved: {
            const d = i;
            if (this._devices.has(d.DeviceIndex)) {
              const c = this._devices.get(d.DeviceIndex);
              c == null ? void 0 : c.emitDisconnected(), this._devices.delete(d.DeviceIndex), this.emit("deviceremoved", c);
            }
            break;
          }
          case se.ScanningFinished:
            this._isScanning = false, this.emit("scanningfinished", i);
            break;
        }
      }, this.initializeConnection = () => ue(this, void 0, void 0, function* () {
        this.checkConnector();
        const t = yield this.sendMessage(new se.RequestServerInfo(this._clientName, se.MESSAGE_SPEC_VERSION));
        switch ((0, ke.getMessageClassFromMessage)(t)) {
          case se.ServerInfo: {
            const r = t;
            if (this._logger.Info(`ButtplugClient: Connected to Server ${r.ServerName}`), r.MaxPingTime, r.MessageVersion < se.MESSAGE_SPEC_VERSION) throw yield this._connector.disconnect(), ge.ButtplugError.LogAndError(ge.ButtplugInitError, this._logger, `Server protocol version ${r.MessageVersion} is older than client protocol version ${se.MESSAGE_SPEC_VERSION}. Please update server.`);
            return yield this.requestDeviceList(), true;
          }
          case se.Error: {
            yield this._connector.disconnect();
            const r = t;
            throw ge.ButtplugError.LogAndError(ge.ButtplugInitError, this._logger, `Cannot connect to server. ${r.ErrorMessage}`);
          }
        }
        return false;
      }), this.requestDeviceList = () => ue(this, void 0, void 0, function* () {
        this.checkConnector(), this._logger.Debug("ButtplugClient: ReceiveDeviceList called"), (yield this.sendMessage(new se.RequestDeviceList())).Devices.forEach((r) => {
          if (this._devices.has(r.DeviceIndex)) this._logger.Debug(`ButtplugClient: Device already added: ${r}`);
          else {
            const i = ut.ButtplugClientDevice.fromMsg(r, this.sendDeviceMessageClosure);
            this._logger.Debug(`ButtplugClient: Adding Device: ${i}`), this._devices.set(r.DeviceIndex, i), this.emit("deviceadded", i);
          }
        });
      }), this.shutdownConnection = () => ue(this, void 0, void 0, function* () {
        yield this.stopAllDevices(), this._pingTimer !== null && (clearInterval(this._pingTimer), this._pingTimer = null);
      }), this.sendMsgExpectOk = (t) => ue(this, void 0, void 0, function* () {
        const r = yield this.sendMessage(t);
        switch ((0, ke.getMessageClassFromMessage)(r)) {
          case se.Ok:
            return;
          case se.Error:
            throw ge.ButtplugError.FromError(r);
          default:
            throw ge.ButtplugError.LogAndError(ge.ButtplugMessageError, this._logger, `Message type ${(0, ke.getMessageClassFromMessage)(r).constructor} not handled by SendMsgExpectOk`);
        }
      }), this.sendDeviceMessageClosure = (t, r) => ue(this, void 0, void 0, function* () {
        return yield this.sendDeviceMessage(t, r);
      }), this._clientName = e, this._logger.Debug(`ButtplugClient: Client ${e} created.`);
    }
    get connected() {
      return this._connector !== null && this._connector.Connected;
    }
    get devices() {
      this.checkConnector();
      const e = [];
      return this._devices.forEach((t) => {
        e.push(t);
      }), e;
    }
    get isScanning() {
      return this._isScanning;
    }
    sendDeviceMessage(e, t) {
      return ue(this, void 0, void 0, function* () {
        if (this.checkConnector(), this._devices.get(e.index) === void 0) throw ge.ButtplugError.LogAndError(ge.ButtplugDeviceError, this._logger, `Device ${e.index} not available.`);
        return t.DeviceIndex = e.index, yield this.sendMessage(t);
      });
    }
    sendMessage(e) {
      return ue(this, void 0, void 0, function* () {
        this.checkConnector();
        const t = this._sorter.PrepareOutgoingMessage(e);
        return yield this._connector.send(e), yield t;
      });
    }
    checkConnector() {
      if (!this.connected) throw new Nn.ButtplugClientConnectorException("ButtplugClient not connected");
    }
  }
  We.ButtplugClient = jn;
  var Fe = {}, qe = {};
  var Ue = O && O.__awaiter || function(n, e, t, r) {
    function i(d) {
      return d instanceof t ? d : new t(function(c) {
        c(d);
      });
    }
    return new (t || (t = Promise))(function(d, c) {
      function h(u) {
        try {
          v(r.next(u));
        } catch (p) {
          c(p);
        }
      }
      function l(u) {
        try {
          v(r.throw(u));
        } catch (p) {
          c(p);
        }
      }
      function v(u) {
        u.done ? d(u.value) : i(u.value).then(h, l);
      }
      v((r = r.apply(n, e || [])).next());
    });
  };
  Object.defineProperty(qe, "__esModule", {
    value: true
  });
  qe.ButtplugBrowserWebsocketConnector = void 0;
  const Fn = ze, ct = _e;
  class $n extends Fn.EventEmitter {
    constructor(e) {
      super(), this._url = e, this._websocketConstructor = null, this.connect = () => Ue(this, void 0, void 0, function* () {
        var t;
        const r = new ((t = this._websocketConstructor) !== null && t !== void 0 ? t : WebSocket)(this._url);
        let i, d;
        const c = new Promise((l, v) => {
          i = l, d = v;
        }), h = () => d();
        return r.addEventListener("open", () => Ue(this, void 0, void 0, function* () {
          this._ws = r;
          try {
            yield this.initialize(), this._ws.addEventListener("message", (l) => {
              this.parseIncomingMessage(l);
            }), this._ws.removeEventListener("close", h), this._ws.addEventListener("close", this.disconnect), i();
          } catch (l) {
            console.log(l), d();
          }
        })), r.addEventListener("close", h), c;
      }), this.disconnect = () => Ue(this, void 0, void 0, function* () {
        this.Connected && (this._ws.close(), this._ws = void 0, this.emit("disconnect"));
      }), this.initialize = () => Ue(this, void 0, void 0, function* () {
        return Promise.resolve();
      });
    }
    get Connected() {
      return this._ws !== void 0;
    }
    sendMessage(e) {
      if (!this.Connected) throw new Error("ButtplugBrowserWebsocketConnector not connected");
      this._ws.send("[" + e.toJSON() + "]");
    }
    parseIncomingMessage(e) {
      if (typeof e.data == "string") {
        const t = (0, ct.fromJSON)(e.data);
        this.emit("message", t);
      } else e.data instanceof Blob;
    }
    onReaderLoad(e) {
      const t = (0, ct.fromJSON)(e.target.result);
      this.emit("message", t);
    }
  }
  qe.ButtplugBrowserWebsocketConnector = $n;
  Object.defineProperty(Fe, "__esModule", {
    value: true
  });
  Fe.ButtplugBrowserWebsocketClientConnector = void 0;
  const Gn = qe;
  class kn extends Gn.ButtplugBrowserWebsocketConnector {
    constructor() {
      super(...arguments), this.send = (e) => {
        if (!this.Connected) throw new Error("ButtplugClient not connected");
        this.sendMessage(e);
      };
    }
  }
  Fe.ButtplugBrowserWebsocketClientConnector = kn;
  var Je = {}, Un = function() {
    throw new Error("ws does not work in the browser. Browser clients must use the native WebSocket object");
  };
  Object.defineProperty(Je, "__esModule", {
    value: true
  });
  Je.ButtplugNodeWebsocketClientConnector = void 0;
  const Wn = Fe, zn = Un;
  class qn extends Wn.ButtplugBrowserWebsocketClientConnector {
    constructor() {
      super(...arguments), this._websocketConstructor = zn.WebSocket;
    }
  }
  Je.ButtplugNodeWebsocketClientConnector = qn;
  var Mt = {};
  Object.defineProperty(Mt, "__esModule", {
    value: true
  });
  (function(n) {
    var e = O && O.__createBinding || (Object.create ? function(r, i, d, c) {
      c === void 0 && (c = d);
      var h = Object.getOwnPropertyDescriptor(i, d);
      (!h || ("get" in h ? !i.__esModule : h.writable || h.configurable)) && (h = {
        enumerable: true,
        get: function() {
          return i[d];
        }
      }), Object.defineProperty(r, c, h);
    } : function(r, i, d, c) {
      c === void 0 && (c = d), r[c] = i[d];
    }), t = O && O.__exportStar || function(r, i) {
      for (var d in r) d !== "default" && !Object.prototype.hasOwnProperty.call(i, d) && e(i, r, d);
    };
    Object.defineProperty(n, "__esModule", {
      value: true
    }), t(We, n), t(Be, n), t(Fe, n), t(Je, n), t(je, n), t(Ne, n), t(Mt, n), t(me, n), t(_e, n), t(ve, n), t(ee, n);
  })(dt);
  ye = (_a = class extends Qe {
    constructor() {
      super(), this._connected = false, this.initialize = async () => {
      }, this.connect = async () => {
        await ye.maybeLoadWasm(), this.client = ye.wasmInstance.buttplug_create_embedded_wasm_server((e) => {
          this.emitMessage(e);
        }, this.serverPtr), this._connected = true;
      }, this.disconnect = async () => {
      }, this.send = (e) => {
        ye.wasmInstance.buttplug_client_send_json_message(this.client, new TextEncoder().encode("[" + e.toJSON() + "]"), (t) => {
          this.emitMessage(t);
        });
      }, this.emitMessage = (e) => {
        let t = new TextDecoder().decode(e);
        this.emit("message", dt.fromJSON(t));
      };
    }
    get Connected() {
      return this._connected;
    }
  }, _a._loggingActivated = false, _a.maybeLoadWasm = async () => {
    if (ye.wasmInstance == null) {
      const e = await import("./buttplug_wasm-Btty3UUZ.js");
      await e.default("/wasm/buttplug_wasm_bg.wasm"), ye.wasmInstance = e;
    }
  }, _a.activateLogging = async (e = "debug") => {
    if (await ye.maybeLoadWasm(), _a._loggingActivated) {
      console.log("Logging already activated, ignoring.");
      return;
    }
    console.log("Turning on logging."), ye.wasmInstance.buttplug_activate_env_logger(e);
  }, _a);
})();
export {
  ye as ButtplugWasmClientConnector,
  __tla
};
