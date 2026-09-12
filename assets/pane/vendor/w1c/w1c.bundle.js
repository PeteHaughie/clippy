(()=>{var f=(i,t,e)=>()=>{if(e)throw e[0];try{return i&&(t=i(i=0)),t}catch(o){throw e=[o],o}};var Sa=(i,t)=>()=>{try{return t||i((t={exports:{}}).exports,t),t.exports}catch(e){throw t=0,e}};var Ur=f(()=>{});var Ne,Le,ur,Fr,he,Gr,h,Jr,vr,wr=f(()=>{Ne=globalThis,Le=Ne.ShadowRoot&&(Ne.ShadyCSS===void 0||Ne.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ur=Symbol(),Fr=new WeakMap,he=class{constructor(t,e,o){if(this._$cssResult$=!0,o!==ur)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(Le&&t===void 0){let o=e!==void 0&&e.length===1;o&&(t=Fr.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),o&&Fr.set(e,t))}return t}toString(){return this.cssText}},Gr=i=>new he(typeof i=="string"?i:i+"",void 0,ur),h=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((o,a,r)=>o+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(a)+i[r+1],i[0]);return new he(e,i,ur)},Jr=(i,t)=>{if(Le)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let o=document.createElement("style"),a=Ne.litNonce;a!==void 0&&o.setAttribute("nonce",a),o.textContent=e.cssText,i.appendChild(o)}},vr=Le?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let o of t.cssRules)e+=o.cssText;return Gr(e)})(i):i});var za,Ea,Aa,Ca,Oa,Ma,De,Kr,Ta,Ra,pe,fe,Ie,Xr,j,ue=f(()=>{wr();wr();({is:za,defineProperty:Ea,getOwnPropertyDescriptor:Aa,getOwnPropertyNames:Ca,getOwnPropertySymbols:Oa,getPrototypeOf:Ma}=Object),De=globalThis,Kr=De.trustedTypes,Ta=Kr?Kr.emptyScript:"",Ra=De.reactiveElementPolyfillSupport,pe=(i,t)=>i,fe={toAttribute(i,t){switch(t){case Boolean:i=i?Ta:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},Ie=(i,t)=>!za(i,t),Xr={attribute:!0,type:String,converter:fe,reflect:!1,useDefault:!1,hasChanged:Ie};Symbol.metadata??=Symbol("metadata"),De.litPropertyMetadata??=new WeakMap;j=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=Xr){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let o=Symbol(),a=this.getPropertyDescriptor(t,o,e);a!==void 0&&Ea(this.prototype,t,a)}}static getPropertyDescriptor(t,e,o){let{get:a,set:r}=Aa(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:a,set(n){let s=a?.call(this);r?.call(this,n),this.requestUpdate(t,s,o)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Xr}static _$Ei(){if(this.hasOwnProperty(pe("elementProperties")))return;let t=Ma(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(pe("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(pe("properties"))){let e=this.properties,o=[...Ca(e),...Oa(e)];for(let a of o)this.createProperty(a,e[a])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[o,a]of e)this.elementProperties.set(o,a)}this._$Eh=new Map;for(let[e,o]of this.elementProperties){let a=this._$Eu(e,o);a!==void 0&&this._$Eh.set(a,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let o=new Set(t.flat(1/0).reverse());for(let a of o)e.unshift(vr(a))}else t!==void 0&&e.push(vr(t));return e}static _$Eu(t,e){let o=e.attribute;return o===!1?void 0:typeof o=="string"?o:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let o of e.keys())this.hasOwnProperty(o)&&(t.set(o,this[o]),delete this[o]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Jr(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,o){this._$AK(t,o)}_$ET(t,e){let o=this.constructor.elementProperties.get(t),a=this.constructor._$Eu(t,o);if(a!==void 0&&o.reflect===!0){let r=(o.converter?.toAttribute!==void 0?o.converter:fe).toAttribute(e,o.type);this._$Em=t,r==null?this.removeAttribute(a):this.setAttribute(a,r),this._$Em=null}}_$AK(t,e){let o=this.constructor,a=o._$Eh.get(t);if(a!==void 0&&this._$Em!==a){let r=o.getPropertyOptions(a),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:fe;this._$Em=a;let s=n.fromAttribute(e,r.type);this[a]=s??this._$Ej?.get(a)??s,this._$Em=null}}requestUpdate(t,e,o,a=!1,r){if(t!==void 0){let n=this.constructor;if(a===!1&&(r=this[t]),o??=n.getPropertyOptions(t),!((o.hasChanged??Ie)(r,e)||o.useDefault&&o.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,o))))return;this.C(t,e,o)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:o,reflect:a,wrapped:r},n){o&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),r!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||o||(e=void 0),this._$AL.set(t,e)),a===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[a,r]of this._$Ep)this[a]=r;this._$Ep=void 0}let o=this.constructor.elementProperties;if(o.size>0)for(let[a,r]of o){let{wrapped:n}=r,s=this[a];n!==!0||this._$AL.has(a)||s===void 0||this.C(a,void 0,r,s)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(o=>o.hostUpdate?.()),this.update(e)):this._$EM()}catch(o){throw t=!1,this._$EM(),o}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};j.elementStyles=[],j.shadowRootOptions={mode:"open"},j[pe("elementProperties")]=new Map,j[pe("finalized")]=new Map,Ra?.({ReactiveElement:j}),(De.reactiveElementVersions??=[]).push("2.1.2")});function so(i,t){if(!_r(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return Zr!==void 0?Zr.createHTML(t):t}function ot(i,t,e=i,o){if(t===H)return t;let a=o!==void 0?e._$Co?.[o]:e._$Cl,r=me(t)?void 0:t._$litDirective$;return a?.constructor!==r&&(a?._$AO?.(!1),r===void 0?a=void 0:(a=new r(i),a._$AT(i,e,o)),o!==void 0?(e._$Co??=[])[o]=a:e._$Cl=a),a!==void 0&&(t=ot(i,a._$AS(i,t.values),a,o)),t}var kr,Yr,Ve,Zr,ao,I,io,Pa,U,we,me,_r,ja,mr,ve,Qr,to,B,eo,ro,no,Sr,l,Qa,ti,H,b,oo,q,Ha,be,br,ge,at,gr,xr,yr,$r,Wa,co,xe=f(()=>{kr=globalThis,Yr=i=>i,Ve=kr.trustedTypes,Zr=Ve?Ve.createPolicy("lit-html",{createHTML:i=>i}):void 0,ao="$lit$",I=`lit$${Math.random().toFixed(9).slice(2)}$`,io="?"+I,Pa=`<${io}>`,U=document,we=()=>U.createComment(""),me=i=>i===null||typeof i!="object"&&typeof i!="function",_r=Array.isArray,ja=i=>_r(i)||typeof i?.[Symbol.iterator]=="function",mr=`[ 	
\f\r]`,ve=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Qr=/-->/g,to=/>/g,B=RegExp(`>|${mr}(?:([^\\s"'>=/]+)(${mr}*=${mr}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),eo=/'/g,ro=/"/g,no=/^(?:script|style|textarea|title)$/i,Sr=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),l=Sr(1),Qa=Sr(2),ti=Sr(3),H=Symbol.for("lit-noChange"),b=Symbol.for("lit-nothing"),oo=new WeakMap,q=U.createTreeWalker(U,129);Ha=(i,t)=>{let e=i.length-1,o=[],a,r=t===2?"<svg>":t===3?"<math>":"",n=ve;for(let s=0;s<e;s++){let u=i[s],y,k,x=-1,P=0;for(;P<u.length&&(n.lastIndex=P,k=n.exec(u),k!==null);)P=n.lastIndex,n===ve?k[1]==="!--"?n=Qr:k[1]!==void 0?n=to:k[2]!==void 0?(no.test(k[2])&&(a=RegExp("</"+k[2],"g")),n=B):k[3]!==void 0&&(n=B):n===B?k[0]===">"?(n=a??ve,x=-1):k[1]===void 0?x=-2:(x=n.lastIndex-k[2].length,y=k[1],n=k[3]===void 0?B:k[3]==='"'?ro:eo):n===ro||n===eo?n=B:n===Qr||n===to?n=ve:(n=B,a=void 0);let D=n===B&&i[s+1].startsWith("/>")?" ":"";r+=n===ve?u+Pa:x>=0?(o.push(y),u.slice(0,x)+ao+u.slice(x)+I+D):u+I+(x===-2?s:D)}return[so(i,r+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),o]},be=class i{constructor({strings:t,_$litType$:e},o){let a;this.parts=[];let r=0,n=0,s=t.length-1,u=this.parts,[y,k]=Ha(t,e);if(this.el=i.createElement(y,o),q.currentNode=this.el.content,e===2||e===3){let x=this.el.content.firstChild;x.replaceWith(...x.childNodes)}for(;(a=q.nextNode())!==null&&u.length<s;){if(a.nodeType===1){if(a.hasAttributes())for(let x of a.getAttributeNames())if(x.endsWith(ao)){let P=k[n++],D=a.getAttribute(x).split(I),We=/([.?@])?(.*)/.exec(P);u.push({type:1,index:r,name:We[2],strings:D,ctor:We[1]==="."?gr:We[1]==="?"?xr:We[1]==="@"?yr:at}),a.removeAttribute(x)}else x.startsWith(I)&&(u.push({type:6,index:r}),a.removeAttribute(x));if(no.test(a.tagName)){let x=a.textContent.split(I),P=x.length-1;if(P>0){a.textContent=Ve?Ve.emptyScript:"";for(let D=0;D<P;D++)a.append(x[D],we()),q.nextNode(),u.push({type:2,index:++r});a.append(x[P],we())}}}else if(a.nodeType===8)if(a.data===io)u.push({type:2,index:r});else{let x=-1;for(;(x=a.data.indexOf(I,x+1))!==-1;)u.push({type:7,index:r}),x+=I.length-1}r++}}static createElement(t,e){let o=U.createElement("template");return o.innerHTML=t,o}};br=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:o}=this._$AD,a=(t?.creationScope??U).importNode(e,!0);q.currentNode=a;let r=q.nextNode(),n=0,s=0,u=o[0];for(;u!==void 0;){if(n===u.index){let y;u.type===2?y=new ge(r,r.nextSibling,this,t):u.type===1?y=new u.ctor(r,u.name,u.strings,this,t):u.type===6&&(y=new $r(r,this,t)),this._$AV.push(y),u=o[++s]}n!==u?.index&&(r=q.nextNode(),n++)}return q.currentNode=U,a}p(t){let e=0;for(let o of this._$AV)o!==void 0&&(o.strings!==void 0?(o._$AI(t,o,e),e+=o.strings.length-2):o._$AI(t[e])),e++}},ge=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,o,a){this.type=2,this._$AH=b,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=o,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=ot(this,t,e),me(t)?t===b||t==null||t===""?(this._$AH!==b&&this._$AR(),this._$AH=b):t!==this._$AH&&t!==H&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):ja(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==b&&me(this._$AH)?this._$AA.nextSibling.data=t:this.T(U.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:o}=t,a=typeof o=="number"?this._$AC(t):(o.el===void 0&&(o.el=be.createElement(so(o.h,o.h[0]),this.options)),o);if(this._$AH?._$AD===a)this._$AH.p(e);else{let r=new br(a,this),n=r.u(this.options);r.p(e),this.T(n),this._$AH=r}}_$AC(t){let e=oo.get(t.strings);return e===void 0&&oo.set(t.strings,e=new be(t)),e}k(t){_r(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,o,a=0;for(let r of t)a===e.length?e.push(o=new i(this.O(we()),this.O(we()),this,this.options)):o=e[a],o._$AI(r),a++;a<e.length&&(this._$AR(o&&o._$AB.nextSibling,a),e.length=a)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let o=Yr(t).nextSibling;Yr(t).remove(),t=o}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},at=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,o,a,r){this.type=1,this._$AH=b,this._$AN=void 0,this.element=t,this.name=e,this._$AM=a,this.options=r,o.length>2||o[0]!==""||o[1]!==""?(this._$AH=Array(o.length-1).fill(new String),this.strings=o):this._$AH=b}_$AI(t,e=this,o,a){let r=this.strings,n=!1;if(r===void 0)t=ot(this,t,e,0),n=!me(t)||t!==this._$AH&&t!==H,n&&(this._$AH=t);else{let s=t,u,y;for(t=r[0],u=0;u<r.length-1;u++)y=ot(this,s[o+u],e,u),y===H&&(y=this._$AH[u]),n||=!me(y)||y!==this._$AH[u],y===b?t=b:t!==b&&(t+=(y??"")+r[u+1]),this._$AH[u]=y}n&&!a&&this.j(t)}j(t){t===b?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},gr=class extends at{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===b?void 0:t}},xr=class extends at{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==b)}},yr=class extends at{constructor(t,e,o,a,r){super(t,e,o,a,r),this.type=5}_$AI(t,e=this){if((t=ot(this,t,e,0)??b)===H)return;let o=this._$AH,a=t===b&&o!==b||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==b&&(o===b||a);a&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},$r=class{constructor(t,e,o){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=o}get _$AU(){return this._$AM._$AU}_$AI(t){ot(this,t)}},Wa=kr.litHtmlPolyfillSupport;Wa?.(be,ge),(kr.litHtmlVersions??=[]).push("3.3.3");co=(i,t,e)=>{let o=e?.renderBefore??t,a=o._$litPart$;if(a===void 0){let r=e?.renderBefore??null;o._$litPart$=a=new ge(t.insertBefore(we(),r),r,void 0,e??{})}return a._$AI(i),a}});var zr,d,Na,lo=f(()=>{ue();ue();xe();xe();zr=globalThis,d=class extends j{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=co(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return H}};d._$litElement$=!0,d.finalized=!0,zr.litElementHydrateSupport?.({LitElement:d});Na=zr.litElementPolyfillSupport;Na?.({LitElement:d});(zr.litElementVersions??=[]).push("4.2.2")});var ho=f(()=>{});var v=f(()=>{ue();xe();lo();ho()});var p,po=f(()=>{p=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)}});function c(i){return(t,e)=>typeof e=="object"?Da(i,t,e):((o,a,r)=>{let n=a.hasOwnProperty(r);return a.constructor.createProperty(r,o),n?Object.getOwnPropertyDescriptor(a,r):void 0})(i,t,e)}var La,Da,Er=f(()=>{ue();La={attribute:!0,type:String,converter:fe,reflect:!1,hasChanged:Ie},Da=(i=La,t,e)=>{let{kind:o,metadata:a}=e,r=globalThis.litPropertyMetadata.get(a);if(r===void 0&&globalThis.litPropertyMetadata.set(a,r=new Map),o==="setter"&&((i=Object.create(i)).wrapped=!0),r.set(e.name,i),o==="accessor"){let{name:n}=e;return{set(s){let u=t.get.call(this);t.set.call(this,s),this.requestUpdate(n,u,i,!0,s)},init(s){return s!==void 0&&this.C(n,void 0,i,s),s}}}if(o==="setter"){let{name:n}=e;return function(s){let u=this[n];t.call(this,s),this.requestUpdate(n,u,i,!0,s)}}throw Error("Unsupported decorator location: "+o)}});function $(i){return c({...i,state:!0,attribute:!1})}var fo=f(()=>{Er();});var uo=f(()=>{});var F,it=f(()=>{F=(i,t,e)=>(e.configurable=!0,e.enumerable=!0,Reflect.decorate&&typeof t!="object"&&Object.defineProperty(i,t,e),e)});function S(i,t){return(e,o,a)=>{let r=n=>n.renderRoot?.querySelector(i)??null;if(t){let{get:n,set:s}=typeof o=="object"?e:a??(()=>{let u=Symbol();return{get(){return this[u]},set(y){this[u]=y}}})();return F(e,o,{get(){let u=n.call(this);return u===void 0&&(u=r(this),(u!==null||this.hasUpdated)&&s.call(this,u)),u}})}return F(e,o,{get(){return r(this)}})}}var vo=f(()=>{it();});var wo=f(()=>{it();});var mo=f(()=>{it();});var bo=f(()=>{it();});var go=f(()=>{it();});var w=f(()=>{po();Er();fo();uo();vo();wo();mo();bo();go()});var G,nt,W,Ar=f(()=>{v();w();G=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},W=(nt=class extends d{constructor(){super(...arguments),this.label="Address",this.value="",this.placeholder="",this.disabled=!1,this.readonly=!1}focus(t){this.input?.focus(t)}render(){return l`
			<label part="chrome" class="chrome">
				<span part="label" class="label"><slot name="label">${this.label}</slot></span>
				<span part="prefix" class="prefix"><slot name="prefix"></slot></span>
				<input
					part="input"
					type="text"
					.value=${this.value}
					placeholder=${this.placeholder}
					?disabled=${this.disabled}
					?readonly=${this.readonly}
					aria-label=${this.label}
					@input=${this.handleInput}
					@change=${this.handleChange} />
				<span part="actions" class="actions"><slot name="actions"></slot></span>
			</label>
		`}handleInput(t){this.value=t.currentTarget.value,this.dispatchEvent(new Event("input",{bubbles:!0,composed:!0}))}handleChange(){this.dispatchEvent(new Event("change",{bubbles:!0,composed:!0}))}},nt.styles=h`
		:host {
			display: inline-block;
			min-width: min(100%, 220px);
			color: var(--w1c-address-field-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto auto minmax(0, 1fr) auto;
			align-items: center;
			gap: var(--w1c-address-field-gap, var(--w1c-space-1, 4px));
			width: 100%;
			padding: var(--w1c-address-field-padding, 2px);
			border: var(--w1c-address-field-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-address-field-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-address-field-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-address-field-background, var(--w1c-window-content-background, #ffffff));
		}

		.label {
			padding-inline: var(--w1c-address-field-label-padding, 2px 4px);
			white-space: nowrap;
			background: var(--w1c-address-field-label-background, transparent);
		}

		.prefix,
		.actions {
			display: inline-flex;
			align-items: center;
			min-width: 0;
		}

		input {
			box-sizing: border-box;
			min-width: 0;
			width: 100%;
			border: 0;
			color: inherit;
			background: transparent;
			font: inherit;
			outline: none;
		}

		input::placeholder {
			color: var(--w1c-address-field-placeholder, var(--w1c-disabled-text, #808080));
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}

		.actions ::slotted(w1c-button) {
			--w1c-button-padding: var(--w1c-address-field-button-padding, 1px 8px);
		}
	`,nt);G([c()],W.prototype,"label",void 0);G([c()],W.prototype,"value",void 0);G([c()],W.prototype,"placeholder",void 0);G([c({type:Boolean,reflect:!0})],W.prototype,"disabled",void 0);G([c({type:Boolean,reflect:!0})],W.prototype,"readonly",void 0);G([S("input")],W.prototype,"input",void 0);W=G([p("w1c-address-field")],W)});var Cr,st,ye,xo=f(()=>{v();w();Cr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},ye=(st=class extends d{constructor(){super(...arguments),this.title="",this.variant="status"}render(){return l`
			<section
				part="chrome"
				class="chrome"
				role=${this.variant==="danger"?"alert":"status"}
				data-variant=${this.variant}>
				<span part="icon" class="icon"><slot name="icon"></slot></span>
				<div part="content" class="content">
					<strong part="title" class="title" ?hidden=${!this.title}>${this.title}</strong>
					<slot></slot>
				</div>
				<span part="actions" class="actions"><slot name="actions"></slot></span>
			</section>
		`}},st.styles=h`
		:host {
			display: block;
			color: var(--w1c-alert-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr) auto;
			align-items: start;
			gap: var(--w1c-alert-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-alert-padding, 8px);
			border: var(--w1c-alert-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-alert-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-alert-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-alert-background, var(--w1c-control-background, #c0c0c0));
			box-shadow: var(
				--w1c-alert-shadow,
				inset -1px -1px 0 var(--w1c-control-shadow, #808080),
				inset 1px 1px 0 var(--w1c-control-highlight, #ffffff)
			);
		}

		.chrome[data-variant='info'] {
			border-color: var(--w1c-alert-info-border, var(--w1c-info-text, #003c8f));
		}

		.chrome[data-variant='success'] {
			border-color: var(--w1c-alert-success-border, var(--w1c-success-text, #0d5c1f));
		}

		.chrome[data-variant='warning'] {
			border-color: var(--w1c-alert-warning-border, var(--w1c-warning-text, #6f4a00));
		}

		.chrome[data-variant='danger'] {
			border-color: var(--w1c-alert-danger-border, var(--w1c-danger-text, #990000));
		}

		.icon,
		.actions {
			display: inline-flex;
			align-items: center;
			min-width: 0;
		}

		.icon:empty,
		.actions:empty {
			display: none;
		}

		.content {
			display: grid;
			gap: var(--w1c-alert-content-gap, 2px);
			min-width: 0;
		}

		.title {
			font-weight: 700;
		}
	`,st);Cr([c()],ye.prototype,"title",void 0);Cr([c({reflect:!0})],ye.prototype,"variant",void 0);ye=Cr([p("w1c-alert")],ye)});var J,ct,N,yo=f(()=>{v();w();J=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},N=(ct=class extends d{constructor(){super(...arguments),this.href="",this.target="",this.rel="",this.variant="split",this.label="",this.hasIcon=!1}render(){let t=l`
			<span part="icon" class="icon" ?hidden=${!this.hasIcon}>
				<slot name="icon" @slotchange=${this.handleIconSlotChange}></slot>
			</span>
			<span part="label" class="label"><slot>${this.label}</slot></span>
		`;return this.href?l`
				<a
					part="chrome"
					class="chrome"
					href=${this.href}
					target=${this.target||void 0}
					rel=${this.rel||void 0}
					data-variant=${this.variant}>
					${t}
				</a>
			`:l`<span part="chrome" class="chrome" data-variant=${this.variant}>${t}</span>`}handleIconSlotChange(t){let e=t.currentTarget;this.hasIcon=e.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},ct.styles=h`
		:host {
			display: inline-block;
			width: var(--w1c-badge-width, 88px);
			height: var(--w1c-badge-height, 31px);
			vertical-align: middle;
			color: var(--w1c-badge-text, #000000);
			font: var(--w1c-badge-font, 700 10px/1 var(--w1c-font-ui, Arial, sans-serif));
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr);
			align-items: stretch;
			width: 100%;
			height: 100%;
			overflow: hidden;
			border: var(--w1c-badge-border, 1px solid #000000);
			background: var(--w1c-badge-background, linear-gradient(#ffffff 0 48%, #d8d8d8 48% 100%));
			color: inherit;
			text-decoration: none;
			text-transform: uppercase;
			image-rendering: pixelated;
		}

		.icon {
			box-sizing: border-box;
			display: grid;
			place-items: center;
			min-width: var(--w1c-badge-icon-width, 25px);
			padding: 1px 2px;
			border-inline-end: var(--w1c-badge-divider, 1px solid #000000);
			background: var(--w1c-badge-icon-background, #000000);
			color: var(--w1c-badge-icon-text, #ffffff);
			font-size: 13px;
			line-height: 1;
		}

		.label {
			box-sizing: border-box;
			display: grid;
			place-items: center;
			min-width: 0;
			padding: 1px 3px;
			text-align: center;
			overflow-wrap: anywhere;
			text-shadow: var(--w1c-badge-label-shadow, 1px 1px 0 #ffffff);
		}

		.chrome[data-variant='plain'] {
			grid-template-columns: minmax(0, 1fr);
		}

		.chrome[data-variant='plain'] .icon {
			display: none;
		}

		.chrome[data-variant='warning'] {
			background: var(
				--w1c-badge-warning-background,
				repeating-linear-gradient(45deg, #ffff00 0 5px, #000000 5px 10px)
			);
			color: var(--w1c-badge-warning-text, #000000);
		}

		.chrome[data-variant='warning'] .label {
			margin: 3px;
			background: var(--w1c-badge-warning-label-background, #ffffff);
			text-shadow: none;
		}

		[hidden] {
			display: none;
		}
	`,ct);J([c()],N.prototype,"href",void 0);J([c()],N.prototype,"target",void 0);J([c()],N.prototype,"rel",void 0);J([c({reflect:!0})],N.prototype,"variant",void 0);J([c()],N.prototype,"label",void 0);J([$()],N.prototype,"hasIcon",void 0);N=J([p("w1c-badge-88x31")],N)});var $o,lt,Be,ko=f(()=>{v();w();$o=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Be=(lt=class extends d{constructor(){super(...arguments),this.speed=1}render(){return l`<span part="text" class="text" style=${`--w1c-blink-duration: ${Math.max(.35,this.speed)}s`}>
			<slot></slot>
		</span>`}},lt.styles=h`
		:host {
			display: inline;
			color: var(--w1c-blink-text, #ff0000);
			font: inherit;
		}

		.text {
			display: inline;
			font-weight: var(--w1c-blink-font-weight, 700);
			text-decoration: var(--w1c-blink-decoration, underline);
			animation: w1c-blink var(--w1c-blink-duration, 1s) steps(1, end) infinite;
		}

		@keyframes w1c-blink {
			50% {
				opacity: 0;
			}
		}

		@media (prefers-reduced-motion: reduce) {
			.text {
				animation: none;
				outline: var(--w1c-blink-reduced-outline, 2px dotted currentColor);
				outline-offset: 2px;
			}
		}
	`,lt);$o([c({type:Number})],Be.prototype,"speed",void 0);Be=$o([p("w1c-blink")],Be)});var Or,dt,$e,qe=f(()=>{v();w();Or=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},$e=(dt=class extends d{constructor(){super(...arguments),this.disabled=!1,this.variant="raised"}render(){return l`
			<button part="control button" type="button" ?disabled=${this.disabled} data-variant=${this.variant}>
				<slot></slot>
			</button>
		`}},dt.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-button-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		button {
			box-sizing: border-box;
			min-height: 24px;
			max-width: 100%;
			display: inline-flex;
			align-items: center;
			justify-content: center;
			gap: var(--w1c-space-1, 4px);
			padding: var(--w1c-button-padding, 3px 12px);
			border-width: var(--w1c-button-border-width, 1px);
			border-style: solid;
			border-color: var(--w1c-button-dark-shadow, var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-button-radius, var(--w1c-radius-1, 0));
			color: inherit;
			background: var(--w1c-button-background, var(--w1c-control-background, #c0c0c0));
			box-shadow: var(
				--w1c-button-shadow-raised,
				inset -1px -1px 0 var(--w1c-button-shadow, var(--w1c-control-shadow, #808080)),
				inset 1px 1px 0 var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff))
			);
			font: inherit;
			text-align: center;
			white-space: nowrap;
			cursor: default;
		}

		button[data-variant='sunken'],
		button:active:not(:disabled) {
			border-color: var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff));
			border-block-start-color: var(--w1c-button-dark-shadow, var(--w1c-control-dark-shadow, #404040));
			border-inline-start-color: var(--w1c-button-dark-shadow, var(--w1c-control-dark-shadow, #404040));
			color: var(--w1c-button-active-text, inherit);
			background: var(
				--w1c-button-active-background,
				var(--w1c-button-background, var(--w1c-control-background, #c0c0c0))
			);
			box-shadow: var(
				--w1c-button-shadow-sunken,
				inset -1px -1px 0 var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff)),
				inset 1px 1px 0 var(--w1c-button-shadow, var(--w1c-control-shadow, #808080))
			);
			padding-block-start: calc(var(--w1c-button-press-offset, 3px) + 1px);
			padding-block-end: calc(var(--w1c-button-press-offset, 3px) - 1px);
		}

		button[data-variant='flat'] {
			border-color: var(--w1c-button-flat-border, var(--w1c-button-shadow, var(--w1c-control-shadow, #808080)));
			background: var(
				--w1c-button-flat-background,
				var(--w1c-button-background, var(--w1c-control-background, #c0c0c0))
			);
			box-shadow: var(--w1c-button-shadow-flat, none);
		}

		button:focus-visible {
			outline: var(--w1c-button-focus-outline, 1px dotted var(--w1c-button-focus, var(--w1c-focus-ring, #000000)));
			outline-offset: -4px;
		}

		button:disabled {
			color: var(--w1c-disabled-text, #808080);
			text-shadow: var(
				--w1c-button-disabled-text-shadow,
				1px 1px 0 var(--w1c-button-highlight, var(--w1c-control-highlight, #ffffff))
			);
		}
	`,dt);Or([c({type:Boolean,reflect:!0})],$e.prototype,"disabled",void 0);Or([c({reflect:!0})],$e.prototype,"variant",void 0);$e=Or([p("w1c-button")],$e)});var V,ht,T,_o=f(()=>{v();w();V=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},T=(ht=class extends d{constructor(){super(...arguments),this.name="",this.value="on",this.checked=!1,this.disabled=!1,this.required=!1,this.invalid=!1}focus(t){this.input?.focus(t)}render(){return l`
			<label part="label">
				<input
					part="control checkbox"
					type="checkbox"
					.name=${this.name}
					.value=${this.value}
					?checked=${this.checked}
					?disabled=${this.disabled}
					?required=${this.required}
					aria-invalid=${this.invalid?"true":"false"}
					@change=${this.handleChange} />
				<span part="text"><slot></slot></span>
			</label>
		`}handleChange(t){this.checked=t.currentTarget.checked,this.dispatchEvent(new Event("change",{bubbles:!0,composed:!0}))}},ht.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-checkbox-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		label {
			display: inline-grid;
			grid-template-columns: auto minmax(0, 1fr);
			align-items: start;
			gap: var(--w1c-checkbox-gap, var(--w1c-space-1, 4px));
		}

		input {
			box-sizing: border-box;
			width: var(--w1c-checkbox-size, 13px);
			height: var(--w1c-checkbox-size, 13px);
			margin: var(--w1c-checkbox-margin, 1px 0 0);
			accent-color: var(--w1c-checkbox-accent, var(--w1c-selection-background, #000080));
		}

		input:focus-visible {
			outline: var(--w1c-checkbox-focus-outline, 1px dotted var(--w1c-focus-ring, #000000));
			outline-offset: 2px;
		}

		:host([invalid]) input {
			outline: var(--w1c-checkbox-invalid-outline, 1px solid var(--w1c-danger-text, #990000));
			outline-offset: 1px;
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}
	`,ht);V([c()],T.prototype,"name",void 0);V([c()],T.prototype,"value",void 0);V([c({type:Boolean,reflect:!0})],T.prototype,"checked",void 0);V([c({type:Boolean,reflect:!0})],T.prototype,"disabled",void 0);V([c({type:Boolean,reflect:!0})],T.prototype,"required",void 0);V([c({type:Boolean,reflect:!0})],T.prototype,"invalid",void 0);V([S("input")],T.prototype,"input",void 0);T=V([p("w1c-checkbox")],T)});var Ue,pt,ft,So=f(()=>{v();w();Ue=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},ft=(pt=class extends d{constructor(){super(...arguments),this.compact=!1,this.hasHeader=!1,this.hasFooter=!1}render(){return l`
			<section part="chrome" class="chrome">
				<header part="header" class="header" ?hidden=${!this.hasHeader}>
					<slot name="header" @slotchange=${this.handleHeaderSlotChange}></slot>
				</header>
				<div part="list" class="list" role="list">
					<slot></slot>
				</div>
				<footer part="footer" class="footer" ?hidden=${!this.hasFooter}>
					<slot name="footer" @slotchange=${this.handleFooterSlotChange}></slot>
				</footer>
			</section>
		`}handleHeaderSlotChange(t){this.hasHeader=this.hasAssignedContent(t)}handleFooterSlotChange(t){this.hasFooter=this.hasAssignedContent(t)}hasAssignedContent(t){return t.currentTarget.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},pt.styles=h`
		:host {
			display: block;
			color: var(--w1c-data-list-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-data-list-font,
				var(
					--w1c-control-font,
					var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.25)
						var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
				)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			min-width: 0;
			border: var(--w1c-data-list-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-data-list-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-data-list-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-data-list-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-data-list-right-edge,
				inset -1px 0 0 var(--w1c-data-list-right-edge-color, var(--w1c-control-shadow, #808080))
			);
			overflow: hidden;
		}

		.header,
		.footer {
			box-sizing: border-box;
			display: flex;
			align-items: center;
			gap: var(--w1c-space-2, 8px);
			padding: var(--w1c-data-list-header-padding, 4px 6px);
			background: var(--w1c-data-list-chrome-background, var(--w1c-surface, #c0c0c0));
		}

		.header {
			border-block-end: var(--w1c-data-list-divider, 1px solid var(--w1c-control-shadow, #808080));
			font-weight: 700;
		}

		.footer {
			border-block-start: var(--w1c-data-list-divider, 1px solid var(--w1c-control-shadow, #808080));
		}

		.list {
			display: grid;
			min-width: 0;
		}

		::slotted(*) {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: var(--w1c-data-list-row-columns, minmax(0, 1fr) auto);
			align-items: center;
			gap: var(--w1c-data-list-row-gap, var(--w1c-space-2, 8px));
			min-width: 0;
			padding: var(--w1c-data-list-row-padding, 5px 6px);
			border-block-end: var(--w1c-data-list-row-border, 1px solid rgb(0 0 0 / 0.12));
			border-inline-end: var(--w1c-data-list-row-right-border, 1px solid var(--w1c-control-shadow, #808080));
			color: inherit;
			text-decoration: none;
			background: var(--w1c-data-list-row-background, transparent);
		}

		:host([compact]) ::slotted(*) {
			padding: var(--w1c-data-list-compact-row-padding, 2px 4px);
		}

		::slotted(:hover) {
			background: var(--w1c-data-list-row-hover-background, rgb(0 0 0 / 0.05));
		}

		::slotted([aria-selected='true']),
		::slotted([selected]) {
			color: var(--w1c-data-list-selected-text, var(--w1c-active-titlebar-text, #ffffff));
			background: var(--w1c-data-list-selected-background, var(--w1c-active-titlebar, #000080));
		}

		[hidden] {
			display: none;
		}
	`,pt);Ue([c({type:Boolean,reflect:!0})],ft.prototype,"compact",void 0);Ue([$()],ft.prototype,"hasHeader",void 0);Ue([$()],ft.prototype,"hasFooter",void 0);ft=Ue([p("w1c-data-list")],ft)});var ke,ut,K,zo=f(()=>{v();w();ke=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},K=(ut=class extends d{constructor(){super(...arguments),this.compact=!1,this.striped=!1,this.hasCaption=!1,this.hasFoot=!1}render(){return l`
			<div part="chrome" class="chrome">
				<div part="table" class="table" role="table">
					<div part="caption" class="caption" ?hidden=${!this.hasCaption}>
						<slot name="caption" @slotchange=${this.handleCaptionSlotChange}></slot>
					</div>
					<div part="head" class="head" role="rowgroup">
						<slot name="head"></slot>
					</div>
					<div part="body" class="body" role="rowgroup">
						<slot></slot>
					</div>
					<div part="foot" class="foot" role="rowgroup" ?hidden=${!this.hasFoot}>
						<slot name="foot" @slotchange=${this.handleFootSlotChange}></slot>
					</div>
				</div>
			</div>
		`}handleCaptionSlotChange(t){this.hasCaption=this.hasAssignedContent(t)}handleFootSlotChange(t){this.hasFoot=this.hasAssignedContent(t)}hasAssignedContent(t){return t.currentTarget.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},ut.styles=h`
		:host {
			display: block;
			color: var(--w1c-data-table-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-data-table-font,
				var(
					--w1c-control-font,
					var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.25)
						var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
				)
			);
		}

		.chrome {
			box-sizing: border-box;
			overflow: auto;
			border: var(--w1c-data-table-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-data-table-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-data-table-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-data-table-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-data-table-right-edge,
				inset -1px 0 0 var(--w1c-data-table-right-edge-color, var(--w1c-control-shadow, #808080))
			);
		}

		.table {
			width: 100%;
			min-width: var(--w1c-data-table-min-width, 320px);
			color: inherit;
			font: inherit;
			background: transparent;
		}

		.caption {
			padding: var(--w1c-data-table-caption-padding, 4px 6px);
			text-align: start;
			font-weight: 700;
			background: var(--w1c-data-table-caption-background, var(--w1c-surface, #c0c0c0));
			border-block-end: var(--w1c-data-table-divider, 1px solid var(--w1c-control-shadow, #808080));
		}

		.head {
			background: var(--w1c-data-table-head-background, var(--w1c-surface, #c0c0c0));
		}

		.foot {
			background: var(--w1c-data-table-foot-background, var(--w1c-surface, #c0c0c0));
		}

		::slotted(*) {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: var(--w1c-data-table-columns, repeat(3, minmax(0, 1fr)));
			gap: var(--w1c-data-table-cell-gap, var(--w1c-space-2, 8px));
			min-width: 0;
			padding: var(--w1c-data-table-cell-padding, 4px 6px);
			border-block-end: var(--w1c-data-table-cell-border, 1px solid var(--w1c-control-shadow, #808080));
			border-inline-end: var(--w1c-data-table-row-right-border, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-data-table-row-background, transparent);
			text-align: start;
			vertical-align: top;
		}

		:host([striped]) .body ::slotted(:nth-child(even)) {
			background: var(--w1c-data-table-stripe-background, rgb(0 0 0 / 0.04));
		}

		::slotted([aria-selected='true']),
		::slotted([selected]) {
			color: var(--w1c-data-table-selected-text, var(--w1c-active-titlebar-text, #ffffff));
			background: var(--w1c-data-table-selected-background, var(--w1c-active-titlebar, #000080));
		}

		:host([compact]) ::slotted(*) {
			padding: var(--w1c-data-table-compact-cell-padding, 2px 4px);
		}

		[hidden] {
			display: none;
		}
	`,ut);ke([c({type:Boolean,reflect:!0})],K.prototype,"compact",void 0);ke([c({type:Boolean,reflect:!0})],K.prototype,"striped",void 0);ke([$()],K.prototype,"hasCaption",void 0);ke([$()],K.prototype,"hasFoot",void 0);K=ke([p("w1c-data-table")],K)});var Fe,vt,wt,Eo=f(()=>{v();w();Fe=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},wt=(vt=class extends d{constructor(){super(...arguments),this.href="",this.label="",this.selected=!1}render(){let t=l`
			<span part="icon" class="icon"><slot name="icon"></slot></span>
			<span part="label" class="label"><slot>${this.label}</slot></span>
		`;return this.href?l`
				<a
					part="control"
					class="control"
					href=${this.href}
					aria-label=${this.label||void 0}
					aria-current=${this.selected?"true":void 0}>
					${t}
				</a>
			`:l`
			<button
				part="control"
				class="control"
				type="button"
				aria-label=${this.label||void 0}
				aria-pressed=${this.selected?"true":"false"}>
				${t}
			</button>
		`}},vt.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-desktop-icon-text, #ffffff);
			font: var(
				--w1c-desktop-icon-font,
				var(--w1c-font-size-1, 12px) / var(--w1c-line-tight, 1.2) var(--w1c-font-ui, sans-serif)
			);
		}

		.control {
			box-sizing: border-box;
			width: var(--w1c-desktop-icon-width);
			min-height: 64px;
			display: grid;
			justify-items: center;
			align-content: start;
			gap: var(--w1c-space-1, 4px);
			padding: var(--w1c-desktop-icon-padding, 6px 4px);
			border: 1px solid transparent;
			color: inherit;
			background: transparent;
			border-radius: var(--w1c-desktop-icon-radius, 0);
			font: inherit;
			text-align: center;
			text-decoration: none;
			text-shadow: var(--w1c-desktop-icon-text-shadow, 1px 1px 0 var(--w1c-desktop-icon-shadow, rgb(0 0 0 / 0.8)));
			cursor: default;
		}

		.icon {
			display: inline-grid;
			place-items: center;
			width: var(--w1c-desktop-icon-size);
			height: var(--w1c-desktop-icon-size);
			color: var(--w1c-desktop-icon-text);
		}

		.icon ::slotted(img),
		.icon ::slotted(svg),
		.icon ::slotted(w1c-icon) {
			width: 100%;
			height: 100%;
			image-rendering: var(--w1c-desktop-icon-rendering, auto);
		}

		.label {
			max-width: 100%;
			padding: var(--w1c-desktop-icon-label-padding, 1px 2px);
			overflow-wrap: anywhere;
		}

		.control:hover,
		.control:focus-visible,
		:host([selected]) .control {
			color: var(--w1c-desktop-icon-selection-text, var(--w1c-active-titlebar-text, #ffffff));
			background: color-mix(
				in srgb,
				var(--w1c-desktop-icon-selection, var(--w1c-active-titlebar, #000080)) 72%,
				transparent
			);
			outline: var(
				--w1c-desktop-icon-outline,
				1px dotted var(--w1c-desktop-icon-selection-text, var(--w1c-active-titlebar-text, #ffffff))
			);
			outline-offset: -2px;
		}

		.control:focus-visible {
			outline-style: solid;
		}
	`,vt);Fe([c()],wt.prototype,"href",void 0);Fe([c()],wt.prototype,"label",void 0);Fe([c({type:Boolean,reflect:!0})],wt.prototype,"selected",void 0);wt=Fe([p("w1c-desktop-icon")],wt)});var Mr,mt,_e,Ge=f(()=>{v();w();Mr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},_e=(mt=class extends d{constructor(){super(...arguments),this.title="",this.hasTitleSlotContent=!1}render(){return l`
			<header part="chrome titlebar">
				<span part="icon" class="icon"><slot name="icon"></slot></span>
				<span part="title" class="title">
					<slot @slotchange=${this.handleTitleSlotChange}></slot>${this.hasTitleSlotContent?b:this.title}
				</span>
				<span part="controls" class="controls"><slot name="controls"></slot></span>
			</header>
		`}handleTitleSlotChange(t){let e=t.currentTarget;this.hasTitleSlotContent=e.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.TEXT_NODE?!!o.textContent?.trim():o instanceof HTMLElement||o instanceof SVGElement)}},mt.styles=h`
		:host {
			display: block;
			min-width: 0;
			color: var(--w1c-titlebar-text, var(--w1c-active-titlebar-text, #ffffff));
			font: var(
				--w1c-titlebar-font,
				700 var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-heading, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		header {
			box-sizing: border-box;
			min-height: var(--w1c-titlebar-height, 22px);
			display: grid;
			grid-template-columns: var(--w1c-titlebar-columns, auto minmax(0, 1fr) auto);
			align-items: center;
			gap: var(--w1c-space-1, 4px);
			padding: var(--w1c-titlebar-padding, 2px 3px);
			border-block-end: var(--w1c-titlebar-border-block-end, 0);
			background: var(--w1c-titlebar-background, var(--w1c-active-titlebar, #000080));
			text-shadow: var(--w1c-titlebar-text-shadow, none);
		}

		.icon,
		.controls {
			display: inline-flex;
			align-items: center;
			min-width: 0;
		}

		.title {
			min-width: 0;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
			padding: var(--w1c-titlebar-title-padding, 0);
			background: var(--w1c-titlebar-title-background, transparent);
			text-align: var(--w1c-titlebar-title-align, start);
		}
	`,mt);Mr([c()],_e.prototype,"title",void 0);Mr([$()],_e.prototype,"hasTitleSlotContent",void 0);_e=Mr([p("w1c-titlebar")],_e)});var Je,bt,gt,Ao=f(()=>{v();w();qe();Ge();Je=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},gt=(bt=class extends d{constructor(){super(...arguments),this.title="Dialog",this.variant="window",this.hasIcon=!1}render(){return l`
			<section
				part="chrome"
				class="chrome"
				role=${this.variant==="alert"?"alertdialog":"dialog"}
				aria-label=${this.title}>
				<slot name="titlebar">
					<w1c-titlebar
						part="titlebar"
						exportparts="chrome: titlebar-chrome, titlebar, icon, title, controls"
						.title=${this.title}></w1c-titlebar>
				</slot>
				<div part="body" class="body" data-has-icon=${this.hasIcon?"true":"false"}>
					<span part="icon" class="icon"><slot name="icon" @slotchange=${this.handleIconSlotChange}></slot></span>
					<div part="content" class="content"><slot></slot></div>
				</div>
				<footer part="actions" class="actions">
					<slot name="actions">
						<w1c-button>OK</w1c-button>
					</slot>
				</footer>
			</section>
		`}handleIconSlotChange(t){let e=t.currentTarget;this.hasIcon=e.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},bt.styles=h`
		:host {
			display: block;
			width: min(var(--w1c-dialog-width, 420px), 100%);
			color: var(--w1c-dialog-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-rows: auto minmax(0, 1fr) auto;
			border: var(
				--w1c-dialog-border,
				1px solid var(--w1c-dialog-dark-shadow, var(--w1c-control-dark-shadow, #404040))
			);
			border-block-start-color: var(--w1c-dialog-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-dialog-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-dialog-radius, var(--w1c-window-radius, var(--w1c-radius-1, 0)));
			background: var(--w1c-dialog-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(
				--w1c-dialog-shadow,
				inset -1px -1px 0 var(--w1c-dialog-shadow-color, var(--w1c-control-shadow, #808080)),
				inset 1px 1px 0 var(--w1c-dialog-highlight, var(--w1c-control-highlight, #ffffff)),
				var(--w1c-dialog-shadow-outer, var(--w1c-shadow-window, 2px 2px 0 rgb(0 0 0 / 0.35)))
			);
			overflow: hidden;
		}

		.body {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr);
			gap: var(--w1c-dialog-body-gap, var(--w1c-space-3, 12px));
			padding: var(--w1c-dialog-body-padding, 16px);
			background: var(--w1c-dialog-background, var(--w1c-window-content-background, #ffffff));
		}

		.body[data-has-icon='false'] {
			grid-template-columns: minmax(0, 1fr);
		}

		.icon {
			display: inline-grid;
			place-items: start center;
			min-width: var(--w1c-dialog-icon-column, 32px);
			color: var(--w1c-dialog-icon-color, currentColor);
		}

		.body[data-has-icon='false'] .icon {
			display: none;
		}

		.content {
			min-width: 0;
		}

		.content ::slotted(*) {
			margin-block-start: 0;
		}

		.actions {
			box-sizing: border-box;
			display: flex;
			flex-wrap: wrap;
			justify-content: flex-end;
			gap: var(--w1c-space-2, 8px);
			padding: var(--w1c-dialog-actions-padding, 0 16px 16px);
			background: var(--w1c-dialog-background, var(--w1c-window-content-background, #ffffff));
		}
	`,bt);Je([c()],gt.prototype,"title",void 0);Je([c({reflect:!0})],gt.prototype,"variant",void 0);Je([$()],gt.prototype,"hasIcon",void 0);gt=Je([p("w1c-dialog")],gt)});var Tr,xt,Se,Co=f(()=>{v();w();Tr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Se=(xt=class extends d{constructor(){super(...arguments),this.orientation="horizontal",this.hasLabel=!1}render(){return l`
			<div
				part="chrome"
				class="chrome"
				role="separator"
				aria-orientation=${this.orientation}
				data-orientation=${this.orientation}>
				<span part="line" class="line"></span>
				<span part="label" class="label" ?hidden=${!this.hasLabel}>
					<slot @slotchange=${this.handleSlotChange}></slot>
				</span>
				<span part="line" class="line"></span>
			</div>
		`}handleSlotChange(t){let e=t.currentTarget;this.hasLabel=e.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},xt.styles=h`
		:host {
			display: block;
			color: var(--w1c-divider-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		:host([orientation='vertical']) {
			display: inline-block;
			align-self: stretch;
			min-height: 1.5em;
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
			align-items: center;
			gap: var(--w1c-divider-gap, var(--w1c-space-2, 8px));
			min-width: 0;
			padding: var(--w1c-divider-padding, var(--w1c-space-1, 4px) 0);
		}

		.line {
			display: block;
			min-width: 0;
			border-block-start: var(--w1c-divider-shadow-line, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end: var(--w1c-divider-highlight-line, 1px solid var(--w1c-control-highlight, #ffffff));
		}

		.label {
			white-space: nowrap;
			color: var(--w1c-divider-label-text, var(--w1c-disabled-text, #808080));
		}

		.chrome[data-orientation='vertical'] {
			grid-template-rows: minmax(0, 1fr) auto minmax(0, 1fr);
			grid-template-columns: auto;
			width: var(--w1c-divider-vertical-width, 8px);
			height: 100%;
			min-height: inherit;
			padding: var(--w1c-divider-vertical-padding, 0 var(--w1c-space-1, 4px));
		}

		.chrome[data-orientation='vertical'] .line {
			width: 0;
			height: 100%;
			border-block: 0;
			border-inline-start: var(--w1c-divider-shadow-line, 1px solid var(--w1c-control-shadow, #808080));
			border-inline-end: var(--w1c-divider-highlight-line, 1px solid var(--w1c-control-highlight, #ffffff));
		}

		.chrome[data-orientation='vertical'] .label {
			writing-mode: vertical-rl;
		}

		[hidden] {
			display: none;
		}
	`,xt);Tr([c({reflect:!0})],Se.prototype,"orientation",void 0);Tr([$()],Se.prototype,"hasLabel",void 0);Se=Tr([p("w1c-divider")],Se)});var Ia,yt,Rr,$t=f(()=>{v();w();Ia=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Rr=(yt=class extends d{render(){return l`<footer part="chrome statusbar content"><slot></slot></footer>`}},yt.styles=h`
		:host {
			display: block;
			color: var(--w1c-control-text, #111111);
			font: var(
				--w1c-statusbar-font,
				var(--w1c-font-size-1, 12px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		footer {
			box-sizing: border-box;
			min-height: var(--w1c-statusbar-height, 22px);
			display: flex;
			align-items: center;
			gap: var(--w1c-space-2, 8px);
			padding: var(--w1c-statusbar-padding, 3px 4px);
			border-block-start: var(--w1c-statusbar-border-block-start, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-statusbar-background, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-statusbar-shadow, none);
		}
	`,yt);Rr=Ia([p("w1c-statusbar")],Rr)});var Va,kt,Pr,_t=f(()=>{v();w();Va=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Pr=(kt=class extends d{render(){return l`<div part="chrome toolbar controls"><slot></slot></div>`}},kt.styles=h`
		:host {
			display: block;
			color: var(--w1c-control-text, #111111);
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		div {
			box-sizing: border-box;
			display: flex;
			flex-wrap: wrap;
			align-items: center;
			gap: var(--w1c-space-1, 4px);
			padding: var(--w1c-toolbar-padding, 4px);
			border-block-start: var(--w1c-toolbar-border-block-start, 1px solid var(--w1c-control-highlight, #ffffff));
			border-block-end: var(--w1c-toolbar-border-block-end, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-toolbar-background, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-toolbar-shadow, none);
		}
	`,kt);Pr=Va([p("w1c-toolbar")],Pr)});var Ke,St,zt,Oo=f(()=>{v();w();Ar();$t();_t();Ke=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},zt=(St=class extends d{constructor(){super(...arguments),this.label="Document browser",this.location="",this.hideSidebar=!1}render(){return l`
			<section part="chrome" class="chrome" role="group" aria-label=${this.label}>
				<slot name="toolbar">
					<w1c-toolbar part="toolbar" exportparts="chrome: toolbar-chrome, toolbar, controls: toolbar-controls">
						<w1c-address-field
							part="location"
							exportparts="chrome: location-chrome, label: location-label, input: location-input"
							label="Location"
							.value=${this.location}></w1c-address-field>
					</w1c-toolbar>
				</slot>
				<div part="body" class="body">
					<aside part="sidebar" class="sidebar" ?hidden=${this.hideSidebar}>
						<slot name="sidebar"></slot>
					</aside>
					<main part="content" class="content">
						<slot></slot>
					</main>
				</div>
				<slot name="statusbar">
					<w1c-statusbar part="statusbar" exportparts="chrome: statusbar-chrome, statusbar, content: statusbar-content">
						Ready
					</w1c-statusbar>
				</slot>
			</section>
		`}},St.styles=h`
		:host {
			display: block;
			min-width: min(100%, 260px);
			color: var(--w1c-document-browser-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-rows: auto minmax(0, 1fr) auto;
			min-height: var(--w1c-document-browser-min-height, 260px);
			border: var(--w1c-document-browser-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-document-browser-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-document-browser-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-document-browser-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-document-browser-shadow, var(--w1c-window-shadow, none));
			overflow: hidden;
		}

		.body {
			display: grid;
			grid-template-columns: minmax(120px, var(--w1c-document-browser-sidebar-width, 180px)) minmax(0, 1fr);
			min-width: 0;
			min-height: 0;
		}

		.sidebar,
		.content {
			box-sizing: border-box;
			min-width: 0;
			min-height: 0;
			overflow: auto;
			background: var(--w1c-document-browser-pane-background, var(--w1c-window-content-background, #ffffff));
		}

		.sidebar {
			padding: var(--w1c-document-browser-sidebar-padding, var(--w1c-space-2, 8px));
			border-inline-end: var(--w1c-document-browser-divider, 1px solid var(--w1c-control-shadow, #808080));
		}

		.content {
			padding: var(--w1c-document-browser-content-padding, var(--w1c-space-3, 12px));
		}

		[hidden] {
			display: none;
		}

		@media (max-width: 520px) {
			.body {
				grid-template-columns: 1fr;
			}

			.sidebar {
				border-inline-end: 0;
				border-block-end: var(--w1c-document-browser-divider, 1px solid var(--w1c-control-shadow, #808080));
			}
		}
	`,St);Ke([c()],zt.prototype,"label",void 0);Ke([c()],zt.prototype,"location",void 0);Ke([c({type:Boolean,reflect:!0,attribute:"hide-sidebar"})],zt.prototype,"hideSidebar",void 0);zt=Ke([p("w1c-document-browser")],zt)});var ze,Et,X,Mo=f(()=>{v();w();ze=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},X=(Et=class extends d{constructor(){super(...arguments),this.method="GET",this.path="/",this.status="Ready",this.variant="neutral"}render(){return l`
			<div part="chrome" class="chrome" data-variant=${this.variant}>
				<span part="method" class="method">${this.method}</span>
				<span part="content" class="content">
					<strong part="path" class="path">${this.path}</strong>
					<span part="status" class="status">${this.status}</span>
					<slot></slot>
				</span>
				<span part="actions" class="actions"><slot name="actions"></slot></span>
			</div>
		`}},Et.styles=h`
		:host {
			display: block;
			color: var(--w1c-endpoint-row-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr) auto;
			align-items: center;
			gap: var(--w1c-endpoint-row-gap, var(--w1c-space-2, 8px));
			min-height: var(--w1c-endpoint-row-min-height, 32px);
			padding: var(--w1c-endpoint-row-padding, 5px 6px);
			border-block-end: var(--w1c-endpoint-row-separator, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-endpoint-row-background, var(--w1c-window-content-background, #ffffff));
		}

		.method {
			min-width: var(--w1c-endpoint-row-method-width, 48px);
			padding: var(--w1c-endpoint-row-method-padding, 2px 5px);
			border: var(--w1c-endpoint-row-method-border, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-endpoint-row-method-background, var(--w1c-control-background, #c0c0c0));
			font-weight: 700;
			text-align: center;
		}

		.chrome[data-variant='good'] .method {
			color: var(--w1c-endpoint-row-good-text, var(--w1c-success-text, #0d5c1f));
		}

		.chrome[data-variant='warning'] .method {
			color: var(--w1c-endpoint-row-warning-text, var(--w1c-warning-text, #6f4a00));
		}

		.chrome[data-variant='danger'] .method {
			color: var(--w1c-endpoint-row-danger-text, var(--w1c-danger-text, #990000));
		}

		.content {
			display: grid;
			gap: var(--w1c-endpoint-row-content-gap, 1px);
			min-width: 0;
		}

		.path {
			overflow-wrap: anywhere;
			font-family: var(--w1c-mono-font-family, 'Courier New', monospace);
			font-size: var(--w1c-endpoint-row-path-size, 13px);
		}

		.status {
			color: var(--w1c-endpoint-row-status-text, var(--w1c-muted-text, #404040));
		}

		.actions {
			display: inline-flex;
			align-items: center;
			gap: var(--w1c-endpoint-row-actions-gap, var(--w1c-space-1, 4px));
			min-width: 0;
		}

		.actions:empty {
			display: none;
		}
	`,Et);ze([c()],X.prototype,"method",void 0);ze([c()],X.prototype,"path",void 0);ze([c()],X.prototype,"status",void 0);ze([c({reflect:!0})],X.prototype,"variant",void 0);X=ze([p("w1c-endpoint-row")],X)});var Ee,At,Y,To=f(()=>{v();w();Ee=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Y=(At=class extends d{constructor(){super(...arguments),this.heading="Guestbook",this.subheading="Thanks for stopping by.",this.hasActions=!1,this.hasFooter=!1}render(){return l`
			<section part="chrome" class="chrome">
				<header part="header" class="header">
					<strong>${this.heading}</strong>
					<span>${this.subheading}</span>
				</header>
				<div part="content" class="content"><slot></slot></div>
				<div part="actions" class="actions" ?hidden=${!this.hasActions}>
					<slot name="actions" @slotchange=${this.handleActionsSlotChange}></slot>
				</div>
				<footer part="footer" class="footer" ?hidden=${!this.hasFooter}>
					<slot name="footer" @slotchange=${this.handleFooterSlotChange}></slot>
				</footer>
			</section>
		`}handleActionsSlotChange(t){this.hasActions=this.hasAssignedContent(t)}handleFooterSlotChange(t){this.hasFooter=this.hasAssignedContent(t)}hasAssignedContent(t){return t.currentTarget.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},At.styles=h`
		:host {
			display: block;
			color: var(--w1c-guestbook-text, var(--w1c-control-text, #000000));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			gap: var(--w1c-guestbook-gap, var(--w1c-space-2, 8px));
			border: var(--w1c-guestbook-border, 4px ridge #ff66cc);
			background: var(--w1c-guestbook-background, #ffffff);
			box-shadow: var(--w1c-guestbook-shadow, 5px 5px 0 #00ffff);
		}

		.header {
			box-sizing: border-box;
			display: grid;
			gap: 2px;
			padding: var(--w1c-guestbook-header-padding, 6px 8px);
			border-block-end: var(--w1c-guestbook-header-border, 3px groove #660066);
			background: var(
				--w1c-guestbook-header-background,
				repeating-linear-gradient(90deg, #ffff00 0 12px, #ff66cc 12px 24px)
			);
			color: var(--w1c-guestbook-header-text, #000000);
			text-align: center;
		}

		.header strong {
			font: var(--w1c-guestbook-heading-font, 700 18px/1.1 var(--w1c-font-heading, cursive));
		}

		.header span {
			font-size: 12px;
		}

		.content {
			box-sizing: border-box;
			display: grid;
			gap: var(--w1c-guestbook-entry-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-guestbook-content-padding, var(--w1c-space-3, 12px));
		}

		::slotted(article),
		::slotted(blockquote) {
			margin: 0;
			padding: var(--w1c-guestbook-entry-padding, var(--w1c-space-2, 8px));
			border: var(--w1c-guestbook-entry-border, 2px dashed #660099);
			background: var(--w1c-guestbook-entry-background, #ffffcc);
		}

		.actions,
		.footer {
			box-sizing: border-box;
			padding: var(--w1c-guestbook-footer-padding, 6px 8px);
			border-block-start: var(--w1c-guestbook-footer-border, 2px dotted #cc6600);
			background: var(--w1c-guestbook-footer-background, #ffffcc);
			text-align: center;
		}

		.actions {
			display: flex;
			flex-wrap: wrap;
			justify-content: center;
			gap: var(--w1c-space-2, 8px);
		}

		[hidden] {
			display: none;
		}
	`,At);Ee([c()],Y.prototype,"heading",void 0);Ee([c()],Y.prototype,"subheading",void 0);Ee([$()],Y.prototype,"hasActions",void 0);Ee([$()],Y.prototype,"hasFooter",void 0);Y=Ee([p("w1c-guestbook-panel")],Y)});var Ro,Ye,Xe,jr=f(()=>{Ro={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Ye=i=>(...t)=>({_$litDirective$:i,values:t}),Xe=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,o){this._$Ct=t,this._$AM=e,this._$Ci=o}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}});var Z,Fn,Po=f(()=>{xe();jr();Z=class extends Xe{constructor(t){if(super(t),this.it=b,t.type!==Ro.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===b||t==null)return this._t=void 0,this.it=t;if(t===H)return t;if(typeof t!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;let e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};Z.directiveName="unsafeHTML",Z.resultType=1;Fn=Ye(Z)});var Ae,jo,Ho=f(()=>{jr();Po();Ae=class extends Z{};Ae.directiveName="unsafeSVG",Ae.resultType=2;jo=Ye(Ae)});var Wo=f(()=>{Ho()});function Qe(i){return Object.hasOwn(Ce,i)?Ce[i]:void 0}var Ct,Ze,m,E,g,Ce,No,Lo,Do,Io=f(()=>{(function(i){i.wikimedia="https://commons.wikimedia.org/wiki/Category:Microsoft_icons",i.bootstrap="https://icons.getbootstrap.com/"})(Ct||(Ct={}));(function(i){i.wikimedia="W1C-normalized icon data. Visual design references Wikimedia Commons Microsoft icon examples.",i.bootstrap="W1C-normalized icon data. Some interface symbols reference Bootstrap Icons."})(Ze||(Ze={}));m=(i,t=16,e=16)=>({width:t,height:e,body:i}),E=(i,t,e="Wikimedia Commons Microsoft icon references",o=Ct.wikimedia,a="W1C icon data: MIT; reference material: mixed Wikimedia Commons file licenses",r=Ze.wikimedia)=>({name:i,category:t,sourceReferenceProject:e,sourceIconName:i,sourceUrl:o,license:a,attribution:r,intendedSize:16}),g=(i,t)=>E(i,t,"Bootstrap Icons",Ct.bootstrap,"W1C icon data: MIT; Bootstrap Icons: MIT",Ze.bootstrap),Ce={"align-left":m('<path d="M2 3h12v1H2zm0 3h9v1H2zm0 3h12v1H2zm0 3h8v1H2z"/>'),at:m('<path d="M13.106 7.222c0-2.967-2.249-5.032-5.482-5.032c-3.35 0-5.646 2.318-5.646 5.702c0 3.493 2.235 5.708 5.762 5.708c.862 0 1.689-.123 2.304-.335v-.862c-.43.199-1.354.328-2.29.328c-2.926 0-4.813-1.88-4.813-4.798c0-2.844 1.921-4.881 4.594-4.881c2.735 0 4.608 1.688 4.608 4.156c0 1.682-.554 2.769-1.416 2.769c-.492 0-.772-.28-.772-.76V5.206H8.923v.834h-.11c-.266-.595-.881-.964-1.6-.964c-1.4 0-2.378 1.162-2.378 2.823c0 1.737.957 2.906 2.379 2.906c.8 0 1.415-.39 1.709-1.087h.11c.081.67.703 1.148 1.503 1.148c1.572 0 2.57-1.415 2.57-3.643zm-7.177.704c0-1.197.54-1.907 1.456-1.907c.93 0 1.524.738 1.524 1.907S8.308 9.84 7.371 9.84c-.895 0-1.442-.725-1.442-1.914" />'),back:m('<path d="M7 3 2 8l5 5V9h7V7H7z"/>'),bold:m('<path d="M8.21 13c2.106 0 3.412-1.087 3.412-2.823c0-1.306-.984-2.283-2.324-2.386v-.055a2.176 2.176 0 0 0 1.852-2.14c0-1.51-1.162-2.46-3.014-2.46H3.843V13zM5.908 4.674h1.696c.963 0 1.517.451 1.517 1.244c0 .834-.629 1.32-1.73 1.32H5.908V4.673zm0 6.788V8.598h1.73c1.217 0 1.88.492 1.88 1.415c0 .943-.643 1.449-1.832 1.449H5.907z" />'),browser:m('<path d="M2 2h12v12H2zm1 1v2h10V3zm0 3v7h10V6zm1-2h1v1H4zm2 0h1v1H6z"/>'),close:m('<path d="m4 3 4 4 4-4 1 1-4 4 4 4-1 1-4-4-4 4-1-1 4-4-4-4z"/>'),computer:m('<path d="M2 2h12v8H2zM3 3v6h10V3zM6 11h4v2h3v1H3v-1h3z"/>'),danger:m('<path d="M0 0h24v24H0z" fill="none"/><g fill="none"><path d="m12.594 23.258l-.012.002l-.071.035l-.02.004l-.014-.004l-.071-.036q-.016-.004-.024.006l-.004.01l-.017.428l.005.02l.01.013l.104.074l.015.004l.012-.004l.104-.074l.012-.016l.004-.017l-.017-.427q-.004-.016-.016-.018m.264-.113l-.014.002l-.184.093l-.01.01l-.003.011l.018.43l.005.012l.008.008l.201.092q.019.005.029-.008l.004-.014l-.034-.614q-.005-.019-.02-.022m-.715.002a.02.02 0 0 0-.027.006l-.006.014l-.034.614q.001.018.017.024l.015-.002l.201-.093l.01-.008l.003-.011l.018-.43l-.003-.012l-.01-.01z"/><path fill="currentColor" d="m13.414 2.808l7.778 7.778a2 2 0 0 1 0 2.829l-7.778 7.778a2 2 0 0 1-2.828 0l-7.778-7.778a2 2 0 0 1 0-2.829l7.778-7.778a2 2 0 0 1 2.828 0M12 4.222L4.222 12L12 19.78L19.778 12zM12.002 15a1 1 0 0 1 .117 1.993l-.117.007a1 1 0 0 1-.119-1.993zM12 8c.867 0 1.538.76 1.43 1.62l-.438 3.504a1 1 0 0 1-1.984 0L10.57 9.62A1.44 1.44 0 0 1 12 8"/></g>',24,24),database:m('<path d="M8 2c3.3 0 6 1 6 2.5v7C14 13 11.3 14 8 14s-6-1-6-2.5v-7C2 3 4.7 2 8 2m0 1C5 3 3 3.8 3 4.5S5 6 8 6s5-.8 5-1.5S11 3 8 3M3 6v2.5C3 9.2 5 10 8 10s5-.8 5-1.5V6C11.9 6.65 10 7 8 7s-3.9-.35-5-1m0 4v1.5C3 12.2 5 13 8 13s5-.8 5-1.5V10c-1.1.65-3 .95-5 .95S4.1 10.65 3 10"/>'),document:m('<path d="M3 1h7l3 3v11H3zM4 2v12h8V5H9V2zM10 2.5V4h1.5zM5 7h6v1H5zm0 3h6v1H5z"/>'),"file-manager":m('<path d="M1 3h5l1 2h8v8H1zm1 1v1h4.38l-1-1zm0 2v6h12V6zM4 8h8v1H4zm0 2h5v1H4z"/>'),folder:m('<path d="M1 4h5l1 2h8v7H1zM2 5v1h4.38l-1-1zM2 7v5h12V7z"/>'),forward:m('<path d="m9 3 5 5-5 5V9H2V7h7z"/>'),github:m('<path d="M8 1.5A6.5 6.5 0 0 0 6 14c.32.06.44-.14.44-.31v-1.1c-1.8.39-2.18-.78-2.18-.78-.3-.75-.72-.95-.72-.95-.58-.4.05-.39.05-.39.65.05 1 .67 1 .67.58.98 1.52.7 1.9.53.06-.42.22-.7.4-.86-1.44-.16-2.95-.72-2.95-3.2 0-.7.25-1.28.66-1.73-.07-.16-.29-.82.06-1.7 0 0 .54-.18 1.78.66A6.2 6.2 0 0 1 8 4.62c.52 0 1.06.07 1.56.21 1.24-.84 1.78-.66 1.78-.66.35.88.13 1.54.06 1.7.41.45.66 1.03.66 1.73 0 2.49-1.52 3.04-2.96 3.2.23.2.44.6.44 1.2v1.7c0 .17.12.37.45.3A6.5 6.5 0 0 0 8 1.5"/>'),globe:m('<path d="M0 0h24v24H0z" fill="none"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 21a9 9 0 1 0 0-18m0 18a9 9 0 1 1 0-18m0 18c2.761 0 3.941-5.163 3.941-9S14.761 3 12 3m0 18c-2.761 0-3.941-5.163-3.941-9S9.239 3 12 3M3.5 9h17m-17 6h17"/>',24,24),highlight:m('<path d="M10.5 1.5 14 5l-6.7 6.7-3.5-3.5zM3 9l4 4H2v-2zm7.5-6.1L5.2 8.2l2.1 2.1 5.3-5.3zM1 14h14v1H1z"/>'),home:m('<path d="m8 2 6 5v7h-4v-4H6v4H2V7zm0 1.3L3 7.45V13h2V9h6v4h2V7.45z"/>'),image:m('<path d="M2 3h12v10H2zM3 4v8h10V4zm2 2h2v2H5zm-1 5 3-3 2 2 1-1 2 2z"/>'),info:m('<path d="M7 3h2v2H7zm-2 4V6h4v6h2v1H5v-1h2V7zM8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1m0 1a6 6 0 1 1 0 12A6 6 0 0 1 8 2"/>'),italic:m('<path d="M6 2h7v1h-2.2L8.2 13H10v1H3v-1h2.2L7.8 3H6z"/>'),list:m('<path d="M2 3h2v2H2zm4 .5h8v1H6zM2 7h2v2H2zm4 .5h8v1H6zM2 11h2v2H2zm4 .5h8v1H6z"/>'),mail:m('<path d="M2 3h12v10H2zm1 1v1l5 3 5-3V4zm0 2.2V12h10V6.2L8 9.2z"/>'),maximize:m('<path d="M3 3h10v10H3zm1 1v8h8V4z"/>'),minimize:m('<path d="M3 11h10v2H3z"/>'),page:m('<path d="M3 1h7l3 3v11H3zm1 1v12h8V5H9V2zm6 .5V4h1.5zM5 6h5v1H5zm0 2h6v1H5zm0 2h6v1H5z"/>'),palette:m('<path d="M8 2a6 6 0 0 0-6 6c0 2.76 2.24 5 5 5h1.5a1.5 1.5 0 0 0 0-3H8a1 1 0 0 1 0-2h2.5A2.5 2.5 0 0 0 13 5.5C13 3.57 10.76 2 8 2M5 7H4V6h1zm2-2H6V4h1zm3 0H9V4h1zm1.5 2H10V6h1.5z"/>'),pdf:m('<path d="M0 0h15v15H0z" fill="none"/><path d="M3.5 8H3V7h.5a.5.5 0 0 1 0 1M7 10V7h.5a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5.5z"/><path fill-rule="evenodd" d="M1 1.5A1.5 1.5 0 0 1 2.5 0h8.207L14 3.293V13.5a1.5 1.5 0 0 1-1.5 1.5h-10A1.5 1.5 0 0 1 1 13.5zM3.5 6H2v5h1V9h.5a1.5 1.5 0 1 0 0-3m4 0H6v5h1.5A1.5 1.5 0 0 0 9 9.5v-2A1.5 1.5 0 0 0 7.5 6m2.5 5V6h3v1h-2v1h1v1h-1v2z" clip-rule="evenodd"/>',15,15),print:m('<path d="M4 1h8v4H4zm1 1v2h6V2zM2 6h12v6h-2v3H4v-3H2zm3 6v2h6v-4H5zm7-4h1v1h-1z"/>'),refresh:m('<path d="M12 3v3H9l1.25-1.25A4 4 0 1 0 12 8h1a5 5 0 1 1-2.05-4.03z"/>'),search:m('<path d="M7 2a5 5 0 1 0 3.1 8.92L13.2 14l.8-.8-3.08-3.1A5 5 0 0 0 7 2m0 1a4 4 0 1 1 0 8A4 4 0 0 1 7 3"/>'),stop:m('<path d="M4 4h8v8H4z"/>'),terminal:m('<path d="M2 3h12v10H2zm1 1v8h10V4zm2 2 3 2-3 2V8.8L6.2 8 5 7.2zm3 4h4v1H8z"/>'),"text-editor":m('<path d="M3 2h10v12H3zm1 1v10h8V3zm1 2h6v1H5zm0 2h6v1H5zm0 2h4v1H5zm5 2h1v1h-1z"/>'),trash:m('<path d="M6 2h4l1 1h3v1H2V3h3zm-2 3h8l-.5 9h-7zm1 1 .4 7h5.2L11 6zM6 7h1v5H6zm3 0h1v5H9z"/>'),underline:m('<path d="M4 2h2v6a2 2 0 1 0 4 0V2h2v6a4 4 0 1 1-8 0zM3 14h10v1H3z"/>'),volume:m('<path d="M2 6h3l4-3v10L5 10H2zm8-1.5c1 .75 1.5 2 1.5 3.5S11 10.75 10 11.5v-1.3c.35-.5.5-1.2.5-2.2S10.35 6.3 10 5.8zm2-2c1.55 1.25 2.5 3.1 2.5 5.5s-.95 4.25-2.5 5.5v-1.3c1-1 1.5-2.35 1.5-4.2S13 4.3 12 3.3z"/>'),warning:m('<path d="M8 1 1 14h14zm0 2.1 5.32 9.9H2.68zM7.5 6h1v4h-1zm0 5h1v1h-1z"/>'),"web-browser":m('<path d="M0 0h24v24H0z" fill="none"/><path d="M16.36 14c.08-.66.14-1.32.14-2s-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2m-5.15 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56M14.34 14H9.66c-.1-.66-.16-1.32-.16-2s.06-1.35.16-2h4.68c.09.65.16 1.32.16 2s-.07 1.34-.16 2M12 19.96c-.83-1.2-1.5-2.53-1.91-3.96h3.82c-.41 1.43-1.08 2.76-1.91 3.96M8 8H5.08A7.92 7.92 0 0 1 9.4 4.44C8.8 5.55 8.35 6.75 8 8m-2.92 8H8c.35 1.25.8 2.45 1.4 3.56A8 8 0 0 1 5.08 16m-.82-2C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2s.06 1.34.14 2M12 4.03c.83 1.2 1.5 2.54 1.91 3.97h-3.82c.41-1.43 1.08-2.77 1.91-3.97M18.92 8h-2.95a15.7 15.7 0 0 0-1.38-3.56c1.84.63 3.37 1.9 4.33 3.56M12 2C6.47 2 2 6.5 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2"/>',24,24),wireless:m('<path d="M8 12.5 6.5 11 8 9.5 9.5 11zM3 7.5a7 7 0 0 1 10 0l-1 1a5.6 5.6 0 0 0-8 0zm-2-2a9.9 9.9 0 0 1 14 0l-1 1a8.5 8.5 0 0 0-12 0z"/>')},No=Object.keys(Ce),Lo={"align-left":g("align-left","formatting"),at:g("at","identity"),back:g("back","action"),bold:g("bold","formatting"),browser:E("browser","app"),close:g("close","window-control"),computer:E("computer","device"),danger:g("danger","status"),database:g("database","object"),document:E("document","file"),"file-manager":E("file-manager","app"),folder:E("folder","file"),forward:g("forward","action"),github:g("github","brand"),globe:g("globe","network"),highlight:g("highlight","formatting"),home:g("home","place"),image:g("image","media"),info:g("info","status"),italic:g("italic","formatting"),list:g("list","formatting"),mail:g("mail","app"),maximize:E("maximize","window-control"),minimize:E("minimize","window-control"),page:E("page","file"),palette:g("palette","tool"),pdf:g("pdf","file"),print:g("print","action"),refresh:g("refresh","action"),search:g("search","action"),stop:g("stop","action"),terminal:E("terminal","app"),"text-editor":E("text-editor","app"),trash:E("trash","place"),underline:g("underline","formatting"),volume:g("volume","status"),warning:g("warning","status"),"web-browser":E("web-browser","app"),wireless:g("wireless","status")},Do={status:"catalog attribution attached per icon",license:"W1C icon data is MIT; Bootstrap Icons are MIT; Wikimedia references have mixed per-file licenses",notes:"The W1C icon set uses original normalized SVG data with two attribution buckets: Wikimedia Commons Microsoft icon references and Bootstrap Icons.",references:[{name:"Wikimedia Commons Microsoft icon references",url:Ct.wikimedia,license:"mixed Wikimedia Commons file licenses",usage:"Visual design inspiration for Microsoft-style file, app, desktop, and window icons"},{name:"Bootstrap Icons",url:Ct.bootstrap,license:"MIT",usage:"Reference for neutral action, formatting, status, and object symbols"}]}});var Hr=f(()=>{Io()});var tr,Ot,Mt,Vo=f(()=>{v();w();Wo();Hr();tr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Mt=(Ot=class extends d{constructor(){super(...arguments),this.name="",this.label=""}render(){let t=this.icon??Qe(this.name);if(!t)return b;let e=t.width??16,o=t.height??16,a=t.left??0,r=t.top??0,n=this.label?b:"true";return l`
			<svg
				part="icon"
				viewBox=${`${a} ${r} ${e} ${o}`}
				width=${e}
				height=${o}
				role=${this.label?"img":b}
				aria-label=${this.label||b}
				aria-hidden=${n}
				fill="currentColor"
				focusable="false">
				${jo(t.body)}
			</svg>
		`}},Ot.styles=h`
		:host {
			display: inline-flex;
			width: var(--w1c-icon-size, 1em);
			height: var(--w1c-icon-size, 1em);
			flex: none;
			color: var(--w1c-icon-color, currentColor);
			line-height: 0;
			vertical-align: -0.125em;
		}

		svg {
			display: block;
			width: 100%;
			height: 100%;
		}
	`,Ot);tr([c()],Mt.prototype,"name",void 0);tr([c()],Mt.prototype,"label",void 0);tr([c({attribute:!1})],Mt.prototype,"icon",void 0);Mt=tr([p("w1c-icon")],Mt)});var er,Tt,Rt,Bo=f(()=>{v();w();er=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Rt=(Tt=class extends d{constructor(){super(...arguments),this.src="",this.alt="",this.caption=""}render(){return l`
			<figure part="chrome" class="chrome">
				${this.src?l`<img part="image" class="image" src=${this.src} alt=${this.alt} />`:l`<div part="image" class="image placeholder" aria-label=${this.alt}></div>`}
				<div part="hotspots" class="hotspots"><slot></slot></div>
				${this.caption?l`<figcaption part="caption" class="caption">${this.caption}</figcaption>`:""}
			</figure>
		`}},Tt.styles=h`
		:host {
			display: block;
			color: var(--w1c-image-map-text, var(--w1c-control-text, #000000));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			position: relative;
			display: inline-block;
			max-width: 100%;
			margin: 0;
			border: var(--w1c-image-map-border, 4px ridge #ffff00);
			background: var(--w1c-image-map-background, #000000);
		}

		.image {
			display: block;
			max-width: 100%;
			height: auto;
			image-rendering: var(--w1c-image-map-rendering, auto);
		}

		.placeholder {
			width: var(--w1c-image-map-placeholder-width, 320px);
			aspect-ratio: var(--w1c-image-map-placeholder-ratio, 4 / 3);
			background:
				linear-gradient(45deg, rgb(255 255 255 / 0.18) 25%, transparent 25% 75%, rgb(255 255 255 / 0.18) 75%),
				linear-gradient(45deg, rgb(255 255 255 / 0.18) 25%, transparent 25% 75%, rgb(255 255 255 / 0.18) 75%), #000066;
			background-position:
				0 0,
				8px 8px;
			background-size: 16px 16px;
		}

		.hotspots {
			position: absolute;
			inset: 0;
		}

		::slotted(a),
		::slotted(button) {
			position: absolute;
			inset-inline-start: var(--x, auto);
			inset-block-start: var(--y, auto);
			width: var(--w, auto);
			height: var(--h, auto);
			box-sizing: border-box;
			border: var(--w1c-image-map-hotspot-border, 2px dashed #ffff00);
			background: var(--w1c-image-map-hotspot-background, rgb(0 0 238 / 0.72));
			color: var(--w1c-image-map-hotspot-text, #ffffff);
			font: var(--w1c-image-map-hotspot-font, 700 12px/1.1 var(--w1c-font-ui, Arial, sans-serif));
			text-align: center;
			text-decoration: none;
		}

		::slotted(a:focus-visible),
		::slotted(button:focus-visible) {
			outline: var(--w1c-image-map-focus, 3px solid #ff0000);
			outline-offset: 2px;
		}

		.caption {
			padding: var(--w1c-image-map-caption-padding, 4px 6px);
			background: var(--w1c-image-map-caption-background, #ffffcc);
			text-align: center;
		}
	`,Tt);er([c()],Rt.prototype,"src",void 0);er([c()],Rt.prototype,"alt",void 0);er([c()],Rt.prototype,"caption",void 0);Rt=er([p("w1c-image-map")],Rt)});var O,Pt,A,qo=f(()=>{v();w();O=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},A=(Pt=class extends d{constructor(){super(...arguments),this.type="text",this.name="",this.value="",this.placeholder="",this.autocomplete="",this.disabled=!1,this.readonly=!1,this.required=!1,this.invalid=!1}focus(t){this.input?.focus(t)}render(){return l`
			<input
				part="control input"
				.type=${this.type}
				.name=${this.name}
				.value=${this.value}
				placeholder=${this.placeholder}
				autocomplete=${this.autocomplete}
				?disabled=${this.disabled}
				?readonly=${this.readonly}
				?required=${this.required}
				aria-invalid=${this.invalid?"true":"false"}
				@input=${this.handleInput}
				@change=${this.handleChange} />
		`}handleInput(t){this.value=t.currentTarget.value,this.dispatchEvent(new Event("input",{bubbles:!0,composed:!0}))}handleChange(){this.dispatchEvent(new Event("change",{bubbles:!0,composed:!0}))}},Pt.styles=h`
		:host {
			display: inline-block;
			min-width: min(100%, 180px);
			color: var(--w1c-input-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		input {
			box-sizing: border-box;
			width: 100%;
			min-height: var(--w1c-input-min-height, 24px);
			padding: var(--w1c-input-padding, 3px 5px);
			border: var(--w1c-input-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-input-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-input-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-input-radius, var(--w1c-radius-1, 0));
			color: inherit;
			background: var(--w1c-input-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-input-shadow,
				inset 1px 1px 0 var(--w1c-control-dark-shadow, #404040),
				inset -1px -1px 0 var(--w1c-control-highlight, #ffffff)
			);
			font: inherit;
		}

		input:focus-visible {
			outline: var(--w1c-input-focus-outline, 1px dotted var(--w1c-focus-ring, #000000));
			outline-offset: -3px;
		}

		input::placeholder {
			color: var(--w1c-input-placeholder, var(--w1c-disabled-text, #808080));
		}

		:host([invalid]) input {
			border-color: var(--w1c-input-invalid-border, var(--w1c-danger-text, #990000));
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}
	`,Pt);O([c()],A.prototype,"type",void 0);O([c()],A.prototype,"name",void 0);O([c()],A.prototype,"value",void 0);O([c()],A.prototype,"placeholder",void 0);O([c()],A.prototype,"autocomplete",void 0);O([c({type:Boolean,reflect:!0})],A.prototype,"disabled",void 0);O([c({type:Boolean,reflect:!0})],A.prototype,"readonly",void 0);O([c({type:Boolean,reflect:!0})],A.prototype,"required",void 0);O([c({type:Boolean,reflect:!0})],A.prototype,"invalid",void 0);O([S("input")],A.prototype,"input",void 0);A=O([p("w1c-input")],A)});var Oe,jt,Q,Uo=f(()=>{v();w();Oe=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Q=(jt=class extends d{constructor(){super(...arguments),this.value=void 0,this.text="",this.indent=2,this.lineNumbers=!1}render(){let t=this.getSource(),e=t.split(`
`);return l`
			<section part="chrome" class="chrome" role="region" aria-label="JSON viewer">
				<div part="toolbar" class="toolbar">
					<slot name="toolbar"></slot>
				</div>
				<div class="source">
					<pre part="gutter" class="gutter" aria-hidden="true" ?hidden=${!this.lineNumbers}>
${e.map((o,a)=>a+1).join(`
`)}</pre
					>
					<pre part="code" class="code"><code>${t}</code></pre>
				</div>
			</section>
		`}getSource(){return this.value!==void 0?this.stringifyValue(this.value):this.text.trim()?this.formatText(this.text):`{
  "status": "ready"
}`}stringifyValue(t){try{return JSON.stringify(t,null,this.indent)??"null"}catch{return String(t)}}formatText(t){try{return JSON.stringify(JSON.parse(t),null,this.indent)}catch{return t}}},jt.styles=h`
		:host {
			display: block;
			color: var(--w1c-json-viewer-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-rows: auto minmax(0, 1fr);
			min-height: var(--w1c-json-viewer-min-height, 180px);
			border: var(--w1c-json-viewer-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-json-viewer-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-json-viewer-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-json-viewer-background, var(--w1c-window-content-background, #ffffff));
			overflow: hidden;
		}

		.toolbar {
			display: flex;
			align-items: center;
			gap: var(--w1c-space-1, 4px);
			padding: var(--w1c-json-viewer-toolbar-padding, 4px 6px);
			border-block-end: var(--w1c-json-viewer-divider, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-json-viewer-toolbar-background, var(--w1c-surface, #c0c0c0));
		}

		.toolbar:empty {
			display: none;
		}

		.source {
			display: grid;
			grid-template-columns: auto minmax(0, 1fr);
			min-width: 0;
			min-height: 0;
			overflow: auto;
		}

		.gutter,
		.code {
			box-sizing: border-box;
			min-height: 100%;
			margin: 0;
			padding: var(--w1c-json-viewer-code-padding, 8px);
			font: var(--w1c-json-viewer-font, var(--w1c-code-font, 12px/1.45 'Courier New', monospace));
			tab-size: 2;
			white-space: pre;
		}

		.gutter {
			user-select: none;
			text-align: end;
			color: var(--w1c-json-viewer-gutter-text, var(--w1c-disabled-text, #808080));
			background: var(--w1c-json-viewer-gutter-background, var(--w1c-surface, #c0c0c0));
			border-inline-end: var(--w1c-json-viewer-divider, 1px solid var(--w1c-control-shadow, #808080));
		}

		.code {
			color: var(--w1c-json-viewer-code-text, inherit);
			background: transparent;
		}

		[hidden] {
			display: none;
		}
	`,jt);Oe([c({attribute:!1})],Q.prototype,"value",void 0);Oe([c()],Q.prototype,"text",void 0);Oe([c({type:Number})],Q.prototype,"indent",void 0);Oe([c({type:Boolean,reflect:!0,attribute:"line-numbers"})],Q.prototype,"lineNumbers",void 0);Q=Oe([p("w1c-json-viewer")],Q)});var Me,Ht,tt,Fo=f(()=>{v();w();Me=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},tt=(Ht=class extends d{constructor(){super(...arguments),this.htmlFor="",this.text="",this.required=!1,this.disabled=!1}render(){return l`
			<label part="label" for=${this.htmlFor} aria-disabled=${this.disabled?"true":"false"}>
				<slot>${this.text}</slot>${this.required?l`<span part="required" aria-hidden="true">*</span>`:null}
			</label>
		`}},Ht.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-label-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		label {
			display: inline-flex;
			align-items: baseline;
			gap: var(--w1c-label-gap, 3px);
		}

		[part='required'] {
			color: var(--w1c-label-required-text, var(--w1c-danger-text, #990000));
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}
	`,Ht);Me([c({attribute:"for",reflect:!0})],tt.prototype,"htmlFor",void 0);Me([c()],tt.prototype,"text",void 0);Me([c({type:Boolean,reflect:!0})],tt.prototype,"required",void 0);Me([c({type:Boolean,reflect:!0})],tt.prototype,"disabled",void 0);tt=Me([p("w1c-label")],tt)});var Wr,Wt,Te,Go=f(()=>{v();w();Wr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Te=(Wt=class extends d{constructor(){super(...arguments),this.datetime="",this.label="Last updated"}render(){return l`
			<p part="chrome" class="chrome">
				<span part="label" class="label">${this.label}:</span>
				<time part="value" class="value" datetime=${this.datetime||void 0}><slot>${this.datetime}</slot></time>
			</p>
		`}},Wt.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-last-updated-text, var(--w1c-control-text, #000000));
			font: var(--w1c-last-updated-font, 700 12px/1.2 var(--w1c-font-ui, Arial, sans-serif));
		}

		.chrome {
			box-sizing: border-box;
			display: inline-flex;
			flex-wrap: wrap;
			gap: 0.35em;
			align-items: baseline;
			margin: 0;
			padding: var(--w1c-last-updated-padding, 3px 6px);
			border: var(--w1c-last-updated-border, 2px dotted #ff66cc);
			background: var(--w1c-last-updated-background, #ffffcc);
		}

		.label {
			color: var(--w1c-last-updated-label-text, #660099);
			text-transform: uppercase;
		}
	`,Wt);Wr([c()],Te.prototype,"datetime",void 0);Wr([c()],Te.prototype,"label",void 0);Te=Wr([p("w1c-last-updated")],Te)});var Nr,Nt,Re,Jo=f(()=>{v();w();Nr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Re=(Nt=class extends d{constructor(){super(...arguments),this.heading="Links",this.columns="auto"}render(){return l`
			<section part="chrome" class="chrome" data-columns=${this.columns}>
				<h2 part="heading" class="heading">${this.heading}</h2>
				<div part="content" class="content"><slot></slot></div>
			</section>
		`}},Nt.styles=h`
		:host {
			display: block;
			color: var(--w1c-link-cluster-text, var(--w1c-control-text, #000000));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			gap: var(--w1c-link-cluster-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-link-cluster-padding, var(--w1c-space-3, 12px));
			border: var(--w1c-link-cluster-border, 3px ridge #00ffff);
			background: var(--w1c-link-cluster-background, #ffffcc);
		}

		.heading {
			margin: 0;
			padding: var(--w1c-link-cluster-heading-padding, 4px 6px);
			background: var(--w1c-link-cluster-heading-background, #ff66cc);
			color: var(--w1c-link-cluster-heading-text, #000000);
			font: var(--w1c-link-cluster-heading-font, 700 17px/1.1 var(--w1c-font-heading, cursive));
			text-align: center;
		}

		.content {
			min-width: 0;
			columns: var(--w1c-link-cluster-columns, 12rem);
		}

		.chrome[data-columns='one'] .content {
			columns: 1;
		}

		.chrome[data-columns='two'] .content {
			columns: 2 10rem;
		}

		::slotted(ul),
		::slotted(ol) {
			margin-block: 0;
			padding-inline-start: 1.25rem;
		}

		::slotted(a) {
			color: var(--w1c-link-cluster-link, #0000ee);
			font-weight: 700;
		}
	`,Nt);Nr([c()],Re.prototype,"heading",void 0);Nr([c({reflect:!0})],Re.prototype,"columns",void 0);Re=Nr([p("w1c-link-cluster")],Re)});var rr,Lt,Dt,Ko=f(()=>{v();w();rr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Dt=(Lt=class extends d{constructor(){super(...arguments),this.direction="left",this.speed=12,this.pauseOnHover=!1}render(){let t=`${Math.max(4,this.speed)}s`;return l`
			<div part="chrome" class="chrome" role="marquee" style=${`--w1c-marquee-duration: ${t}`}>
				<div part="track" class="track" data-direction=${this.direction}><slot></slot></div>
			</div>
		`}},Lt.styles=h`
		:host {
			display: block;
			color: var(--w1c-marquee-text, #ffff00);
			font: var(--w1c-marquee-font, 700 var(--w1c-font-size-2, 16px) / 1.2 var(--w1c-font-heading, cursive));
		}

		.chrome {
			box-sizing: border-box;
			overflow: hidden;
			min-width: 0;
			padding: var(--w1c-marquee-padding, 4px 0);
			border: var(--w1c-marquee-border, 3px inset #660066);
			background: var(--w1c-marquee-background, #000000);
		}

		.track {
			display: inline-block;
			min-width: 100%;
			padding-inline: 100%;
			white-space: nowrap;
			text-align: center;
			text-shadow: var(--w1c-marquee-shadow, 1px 1px 0 #ff0000);
			animation: w1c-marquee-left var(--w1c-marquee-duration, 12s) linear infinite;
		}

		.track[data-direction='right'] {
			animation-name: w1c-marquee-right;
		}

		:host([pause-on-hover]) .chrome:hover .track {
			animation-play-state: paused;
		}

		@keyframes w1c-marquee-left {
			from {
				transform: translateX(0);
			}
			to {
				transform: translateX(-100%);
			}
		}

		@keyframes w1c-marquee-right {
			from {
				transform: translateX(-100%);
			}
			to {
				transform: translateX(0);
			}
		}

		@media (prefers-reduced-motion: reduce) {
			.track {
				display: block;
				padding-inline: var(--w1c-space-2, 8px);
				white-space: normal;
				animation: none;
			}
		}
	`,Lt);rr([c({reflect:!0})],Dt.prototype,"direction",void 0);rr([c({type:Number})],Dt.prototype,"speed",void 0);rr([c({type:Boolean,attribute:"pause-on-hover",reflect:!0})],Dt.prototype,"pauseOnHover",void 0);Dt=rr([p("w1c-marquee")],Dt)});var Xo,It,or,Yo=f(()=>{v();w();Xo=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},or=(It=class extends d{constructor(){super(...arguments),this.label="Menu"}render(){return l`
			<div part="chrome menu" role="menu" aria-label=${this.label}>
				<slot></slot>
			</div>
		`}},It.styles=h`
		:host {
			display: block;
			width: max-content;
			max-width: 100%;
			color: var(--w1c-menu-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		div {
			box-sizing: border-box;
			min-width: var(--w1c-menu-min-width, 160px);
			display: grid;
			gap: var(--w1c-menu-gap, 0);
			padding: var(--w1c-menu-padding, 2px);
			border: var(--w1c-menu-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-menu-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-menu-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-menu-background, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-menu-shadow, var(--w1c-shadow-window, 2px 2px 0 rgb(0 0 0 / 0.35)));
		}
	`,It);Xo([c()],or.prototype,"label",void 0);or=Xo([p("w1c-menu")],or)});var Ba,Vt,Lr,Zo=f(()=>{v();w();Ba=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Lr=(Vt=class extends d{render(){return l`<div part="chrome menubar" role="menubar"><slot></slot></div>`}},Vt.styles=h`
		:host {
			display: block;
			color: var(--w1c-menu-bar-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		div {
			box-sizing: border-box;
			min-height: var(--w1c-menu-bar-height, 24px);
			display: flex;
			align-items: center;
			gap: var(--w1c-menu-bar-gap, 0);
			padding: var(--w1c-menu-bar-padding, 2px);
			border-block-start: var(--w1c-menu-bar-border-block-start, 1px solid var(--w1c-control-highlight, #ffffff));
			border-block-end: var(--w1c-menu-bar-border-block-end, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-menu-bar-background, var(--w1c-surface, #c0c0c0));
		}

		div ::slotted(w1c-menu-item) {
			--w1c-menu-item-height: var(--w1c-menu-bar-item-height, 20px);
			--w1c-menu-item-padding: var(--w1c-menu-bar-item-padding, 2px 8px);
			--w1c-menu-item-gap: var(--w1c-menu-bar-item-gap, var(--w1c-space-1, 4px));
			--w1c-menu-item-active-background: var(
				--w1c-menu-bar-item-active-background,
				var(--w1c-menu-item-active-background, var(--w1c-active-titlebar, #000080))
			);
			--w1c-menu-item-active-text: var(
				--w1c-menu-bar-item-active-text,
				var(--w1c-menu-item-active-text, var(--w1c-active-titlebar-text, #ffffff))
			);
		}
	`,Vt);Lr=Ba([p("w1c-menu-bar")],Lr)});var ar,Bt,qt,Qo=f(()=>{v();w();ar=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},qt=(Bt=class extends d{constructor(){super(...arguments),this.href="",this.disabled=!1,this.checked=!1}render(){let t=l`
			<span part="prefix" class="prefix"><slot name="prefix">${this.checked?"\u2713":""}</slot></span>
			<span part="label" class="label"><slot></slot></span>
			<span part="suffix" class="suffix"><slot name="suffix"></slot></span>
		`;return this.href?l`
				<a
					part="control"
					class="control"
					role=${this.checked?"menuitemcheckbox":"menuitem"}
					href=${this.disabled?void 0:this.href}
					aria-disabled=${this.disabled?"true":void 0}
					aria-checked=${this.checked?"true":void 0}
					@click=${this.handleClick}>
					${t}
				</a>
			`:l`
			<button
				part="control"
				class="control"
				type="button"
				role=${this.checked?"menuitemcheckbox":"menuitem"}
				?disabled=${this.disabled}
				aria-checked=${this.checked?"true":void 0}
				@click=${this.handleClick}>
				${t}
			</button>
		`}handleClick(t){if(this.disabled){t.preventDefault(),t.stopPropagation();return}this.dispatchEvent(new CustomEvent("w1c-menu-item-select",{bubbles:!0,composed:!0}))}},Bt.styles=h`
		:host {
			display: block;
			color: var(--w1c-menu-item-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.control {
			box-sizing: border-box;
			width: 100%;
			min-height: var(--w1c-menu-item-height, 22px);
			display: grid;
			grid-template-columns: minmax(16px, auto) minmax(0, 1fr) auto;
			align-items: center;
			gap: var(--w1c-menu-item-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-menu-item-padding, 2px 8px 2px 4px);
			border: 1px solid transparent;
			color: inherit;
			background: var(--w1c-menu-item-background, transparent);
			font: inherit;
			text-align: start;
			text-decoration: none;
			white-space: nowrap;
			cursor: default;
		}

		.control:hover,
		.control:focus-visible {
			color: var(--w1c-menu-item-active-text, var(--w1c-active-titlebar-text, #ffffff));
			background: var(--w1c-menu-item-active-background, var(--w1c-active-titlebar, #000080));
			outline: none;
		}

		.control:disabled,
		.control[aria-disabled='true'] {
			color: var(--w1c-disabled-text, #808080);
			text-shadow: var(--w1c-menu-item-disabled-shadow, 1px 1px 0 var(--w1c-control-highlight, #ffffff));
		}

		.control:disabled:hover,
		.control[aria-disabled='true']:hover {
			background: transparent;
		}

		.prefix,
		.suffix {
			min-width: 0;
			display: inline-flex;
			align-items: center;
		}

		.suffix {
			justify-content: end;
			color: var(--w1c-menu-item-shortcut-text, currentColor);
		}

		.label {
			min-width: 0;
			overflow: hidden;
			text-overflow: ellipsis;
		}
	`,Bt);ar([c()],qt.prototype,"href",void 0);ar([c({type:Boolean,reflect:!0})],qt.prototype,"disabled",void 0);ar([c({type:Boolean,reflect:!0})],qt.prototype,"checked",void 0);qt=ar([p("w1c-menu-item")],qt)});var ir,Ut,Ft,ta=f(()=>{v();w();ir=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Ft=(Ut=class extends d{constructor(){super(...arguments),this.variant="raised",this.hasHeader=!1,this.hasFooter=!1}render(){return l`
			<section part="chrome" class="chrome" data-variant=${this.variant}>
				<header part="header" class="header" ?hidden=${!this.hasHeader}>
					<slot name="header" @slotchange=${this.handleHeaderSlotChange}></slot>
				</header>
				<div part="content" class="content"><slot></slot></div>
				<footer part="footer" class="footer" ?hidden=${!this.hasFooter}>
					<slot name="footer" @slotchange=${this.handleFooterSlotChange}></slot>
				</footer>
			</section>
		`}handleHeaderSlotChange(t){this.hasHeader=this.hasAssignedContent(t)}handleFooterSlotChange(t){this.hasFooter=this.hasAssignedContent(t)}hasAssignedContent(t){return t.currentTarget.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||!!o.textContent?.trim())}},Ut.styles=h`
		:host {
			display: block;
			color: var(--w1c-panel-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			min-width: 0;
			border: var(--w1c-panel-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-panel-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-panel-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-panel-radius, var(--w1c-radius-1, 0));
			background: var(--w1c-panel-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-panel-shadow, var(--w1c-shadow-raised, none));
			overflow: hidden;
		}

		.chrome[data-variant='sunken'] {
			border-color: var(--w1c-panel-highlight, var(--w1c-control-highlight, #ffffff));
			border-block-start-color: var(--w1c-panel-shadow-color, var(--w1c-control-shadow, #808080));
			border-inline-start-color: var(--w1c-panel-shadow-color, var(--w1c-control-shadow, #808080));
			box-shadow: var(--w1c-panel-shadow-sunken, var(--w1c-shadow-sunken, none));
		}

		.chrome[data-variant='flat'] {
			border-color: var(--w1c-panel-flat-border, var(--w1c-control-shadow, #808080));
			box-shadow: var(--w1c-panel-shadow-flat, none);
		}

		.header,
		.footer {
			box-sizing: border-box;
			display: flex;
			align-items: center;
			gap: var(--w1c-space-2, 8px);
			padding: var(--w1c-panel-header-padding, 4px 6px);
			background: var(--w1c-panel-chrome-background, var(--w1c-surface, #c0c0c0));
		}

		.header {
			border-block-end: var(--w1c-panel-header-border, 1px solid var(--w1c-control-shadow, #808080));
			font: var(
				--w1c-panel-header-font,
				var(
					--w1c-titlebar-font,
					700 var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
						var(--w1c-font-heading, 'MS Sans Serif', Tahoma, sans-serif)
				)
			);
		}

		.footer {
			border-block-start: var(--w1c-panel-footer-border, 1px solid var(--w1c-control-shadow, #808080));
		}

		.content {
			box-sizing: border-box;
			min-width: 0;
			padding: var(--w1c-panel-content-padding, var(--w1c-space-3, 12px));
			background: var(--w1c-panel-background, var(--w1c-window-content-background, #ffffff));
		}

		[hidden] {
			display: none;
		}
	`,Ut);ir([c({reflect:!0})],Ft.prototype,"variant",void 0);ir([$()],Ft.prototype,"hasHeader",void 0);ir([$()],Ft.prototype,"hasFooter",void 0);Ft=ir([p("w1c-panel")],Ft)});var L,Gt,M,ea=f(()=>{v();w();L=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},M=(Gt=class extends d{constructor(){super(...arguments),this.name="",this.value="",this.disabled=!1,this.required=!1,this.invalid=!1,this.options=[]}focus(t){this.select?.focus(t)}firstUpdated(){this.collectOptions()}render(){return l`
			<select
				part="control select"
				.name=${this.name}
				.value=${this.value}
				?disabled=${this.disabled}
				?required=${this.required}
				aria-invalid=${this.invalid?"true":"false"}
				@change=${this.handleChange}>
				${this.options.map(t=>l`
						<option .value=${t.value} ?selected=${this.value===t.value} ?disabled=${t.disabled}>
							${t.label}
						</option>
					`)}
			</select>
			<slot hidden @slotchange=${this.collectOptions}></slot>
		`}collectOptions(){let t=this.optionSlot?.assignedElements({flatten:!0})??[],e=t.filter(o=>o instanceof HTMLOptionElement).map(o=>({value:o.value,label:o.label||o.textContent?.trim()||o.value,disabled:o.disabled}));if(this.options=e,!this.value){let o=t.find(a=>a instanceof HTMLOptionElement&&a.selected);o&&(this.value=o.value)}}handleChange(t){this.value=t.currentTarget.value,this.dispatchEvent(new Event("change",{bubbles:!0,composed:!0}))}},Gt.styles=h`
		:host {
			display: inline-block;
			min-width: min(100%, 180px);
			color: var(--w1c-select-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		select {
			box-sizing: border-box;
			width: 100%;
			min-height: var(--w1c-select-min-height, 24px);
			padding: var(--w1c-select-padding, 2px 24px 2px 5px);
			border: var(--w1c-select-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-select-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-select-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-select-radius, var(--w1c-radius-1, 0));
			color: inherit;
			background: var(--w1c-select-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-select-shadow,
				inset 1px 1px 0 var(--w1c-control-dark-shadow, #404040),
				inset -1px -1px 0 var(--w1c-control-highlight, #ffffff)
			);
			font: inherit;
		}

		select:focus-visible {
			outline: var(--w1c-select-focus-outline, 1px dotted var(--w1c-focus-ring, #000000));
			outline-offset: -3px;
		}

		:host([invalid]) select {
			border-color: var(--w1c-select-invalid-border, var(--w1c-danger-text, #990000));
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}
	`,Gt);L([c()],M.prototype,"name",void 0);L([c()],M.prototype,"value",void 0);L([c({type:Boolean,reflect:!0})],M.prototype,"disabled",void 0);L([c({type:Boolean,reflect:!0})],M.prototype,"required",void 0);L([c({type:Boolean,reflect:!0})],M.prototype,"invalid",void 0);L([S("select")],M.prototype,"select",void 0);L([S("slot")],M.prototype,"optionSlot",void 0);L([$()],M.prototype,"options",void 0);M=L([p("w1c-select")],M)});var Pe,Jt,et,ra=f(()=>{v();w();$t();_t();Pe=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},et=(Jt=class extends d{constructor(){super(...arguments),this.label="Source viewer",this.filename="document.txt",this.text="",this.lineNumbers=!1}render(){let t=this.text||"",e=t?t.split(`
`):[""];return l`
			<section part="chrome" class="chrome" role="group" aria-label=${this.label}>
				<slot name="toolbar">
					<w1c-toolbar
						part="toolbar"
						exportparts="chrome: toolbar-chrome, toolbar, controls: toolbar-controls"></w1c-toolbar>
				</slot>
				<div part="pathbar" class="pathbar">
					<slot name="pathbar">
						<span>${this.filename}</span>
					</slot>
				</div>
				<div part="workspace" class="workspace">
					<pre part="gutter" class="gutter" aria-hidden="true" ?hidden=${!this.lineNumbers}>
${e.map((o,a)=>a+1).join(`
`)}</pre
					>
					<pre part="code" class="code"><code>${t||l`<slot></slot>`}</code></pre>
				</div>
				<slot name="statusbar">
					<w1c-statusbar part="statusbar" exportparts="chrome: statusbar-chrome, statusbar, content: statusbar-content">
						${e.length} ${e.length===1?"line":"lines"}
					</w1c-statusbar>
				</slot>
			</section>
		`}},Jt.styles=h`
		:host {
			display: block;
			min-width: min(100%, 280px);
			color: var(--w1c-source-viewer-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-rows: auto auto minmax(0, 1fr) auto;
			min-height: var(--w1c-source-viewer-min-height, 300px);
			border: var(--w1c-source-viewer-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-source-viewer-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-source-viewer-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-source-viewer-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-source-viewer-shadow, var(--w1c-window-shadow, none));
			overflow: hidden;
		}

		.pathbar {
			box-sizing: border-box;
			display: flex;
			align-items: center;
			min-width: 0;
			min-height: var(--w1c-source-viewer-pathbar-height, 24px);
			padding: var(--w1c-source-viewer-pathbar-padding, 3px 6px);
			border-block-start: var(--w1c-source-viewer-pathbar-highlight, 1px solid var(--w1c-control-highlight, #ffffff));
			border-block-end: var(--w1c-source-viewer-pathbar-border, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-source-viewer-pathbar-background, var(--w1c-surface, #c0c0c0));
			color: var(--w1c-source-viewer-pathbar-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-source-viewer-pathbar-font,
				var(
					--w1c-control-font,
					var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
						var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
				)
			);
		}

		.pathbar ::slotted(*),
		.pathbar span {
			min-width: 0;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}

		.workspace {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr);
			min-width: 0;
			min-height: 0;
			overflow: auto;
			border: var(--w1c-source-viewer-workspace-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-source-viewer-workspace-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-source-viewer-workspace-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-source-viewer-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-source-viewer-right-edge,
				inset -1px 0 0 var(--w1c-source-viewer-right-edge-color, var(--w1c-control-shadow, #808080))
			);
		}

		.gutter,
		.code {
			box-sizing: border-box;
			min-height: 100%;
			margin: 0;
			padding: var(--w1c-source-viewer-code-padding, 8px);
			font: var(--w1c-source-viewer-font, var(--w1c-code-font, 12px/1.45 'Courier New', monospace));
			tab-size: 2;
			white-space: pre;
		}

		.gutter {
			user-select: none;
			text-align: end;
			color: var(--w1c-source-viewer-gutter-text, var(--w1c-disabled-text, #808080));
			background: var(--w1c-source-viewer-gutter-background, var(--w1c-surface, #c0c0c0));
			border-inline-end: var(--w1c-source-viewer-divider, 1px solid var(--w1c-control-shadow, #808080));
		}

		.code {
			min-width: max-content;
			color: var(--w1c-source-viewer-code-text, inherit);
			background: transparent;
		}

		[hidden] {
			display: none;
		}
	`,Jt);Pe([c()],et.prototype,"label",void 0);Pe([c()],et.prototype,"filename",void 0);Pe([c()],et.prototype,"text",void 0);Pe([c({type:Boolean,reflect:!0,attribute:"line-numbers"})],et.prototype,"lineNumbers",void 0);et=Pe([p("w1c-source-viewer")],et)});var nr,Kt,Xt,oa=f(()=>{v();w();nr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Xt=(Kt=class extends d{constructor(){super(...arguments),this.title="Status",this.value="",this.variant="neutral"}render(){return l`
			<section part="chrome" class="chrome" data-variant=${this.variant}>
				<span part="icon" class="icon"><slot name="icon"></slot></span>
				<div part="content" class="content">
					<strong part="title" class="title">${this.title}</strong>
					<span part="value" class="value" ?hidden=${!this.value}>${this.value}</span>
					<slot></slot>
				</div>
				<div part="footer" class="footer"><slot name="footer"></slot></div>
			</section>
		`}},Kt.styles=h`
		:host {
			display: block;
			color: var(--w1c-status-card-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr);
			grid-template-areas:
				'icon content'
				'footer footer';
			gap: var(--w1c-status-card-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-status-card-padding, 10px);
			border: var(--w1c-status-card-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-status-card-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-status-card-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-status-card-background, var(--w1c-control-background, #c0c0c0));
			box-shadow: var(
				--w1c-status-card-shadow,
				inset -1px -1px 0 var(--w1c-control-shadow, #808080),
				inset 1px 1px 0 var(--w1c-control-highlight, #ffffff)
			);
		}

		.chrome[data-variant='good'] {
			border-color: var(--w1c-status-card-good-border, var(--w1c-success-text, #0d5c1f));
		}

		.chrome[data-variant='warning'] {
			border-color: var(--w1c-status-card-warning-border, var(--w1c-warning-text, #6f4a00));
		}

		.chrome[data-variant='danger'] {
			border-color: var(--w1c-status-card-danger-border, var(--w1c-danger-text, #990000));
		}

		.icon {
			grid-area: icon;
			display: inline-flex;
			align-items: center;
			min-width: 0;
		}

		.icon:empty {
			display: none;
		}

		.content {
			grid-area: content;
			display: grid;
			gap: var(--w1c-status-card-content-gap, 2px);
			min-width: 0;
		}

		.title {
			font-weight: 700;
		}

		.value {
			font-size: var(--w1c-status-card-value-size, 18px);
			line-height: 1.1;
		}

		.footer {
			grid-area: footer;
			color: var(--w1c-status-card-footer-text, var(--w1c-muted-text, #404040));
		}

		.footer:empty {
			display: none;
		}
	`,Kt);nr([c()],Xt.prototype,"title",void 0);nr([c()],Xt.prototype,"value",void 0);nr([c({reflect:!0})],Xt.prototype,"variant",void 0);Xt=nr([p("w1c-status-card")],Xt)});var sr,Yt,Zt,aa=f(()=>{v();w();sr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Zt=(Yt=class extends d{constructor(){super(...arguments),this.selected=0,this.handleTabClick=t=>{if(this.isDisabled(t.currentTarget))return;let e=this.getTabs().indexOf(t.currentTarget);e>=0&&this.selectTab(e)},this.handleTabKeydown=t=>{let e=this.getTabs(),o=e.indexOf(t.currentTarget);o<0||this.isDisabled(e[o])||((t.key==="ArrowRight"||t.key==="ArrowDown")&&(t.preventDefault(),this.selectTab(this.getNextEnabledTabIndex(o,1))),(t.key==="ArrowLeft"||t.key==="ArrowUp")&&(t.preventDefault(),this.selectTab(this.getNextEnabledTabIndex(o,-1))),t.key==="Home"&&(t.preventDefault(),this.selectTab(this.getNextEnabledTabIndex(-1,1))),t.key==="End"&&(t.preventDefault(),this.selectTab(this.getNextEnabledTabIndex(e.length,-1))))}}render(){return l`
			<section part="chrome" class="chrome">
				<div part="tablist" class="tablist" role="tablist">
					<slot name="tabs" @slotchange=${this.syncTabs}></slot>
				</div>
				<div part="panels" class="panels">
					<slot @slotchange=${this.syncTabs}></slot>
				</div>
			</section>
		`}updated(t){t.has("selected")&&this.syncTabs()}syncTabs(){let t=this.getTabs(),e=this.getPanels(),o=Math.max(0,Math.min(this.selected,Math.max(t.length-1,0)));if(o!==this.selected){this.selected=o;return}t.forEach((a,r)=>{let n=e[r],s=a.id||`w1c-tab-${r}`,u=n?.id||`w1c-panel-${r}`,y=this.isDisabled(a);a.id=s,a.setAttribute("role","tab"),a.setAttribute("aria-selected",String(r===o)),a.setAttribute("tabindex",r===o&&!y?"0":"-1"),a.setAttribute("aria-controls",u),a.removeEventListener("click",this.handleTabClick),a.addEventListener("click",this.handleTabClick),a.removeEventListener("keydown",this.handleTabKeydown),a.addEventListener("keydown",this.handleTabKeydown),n&&(n.id=u,n.setAttribute("role","tabpanel"),n.setAttribute("aria-labelledby",s),n.toggleAttribute("hidden",r!==o))})}selectTab(t){this.selected=t,this.updateComplete.then(()=>this.getTabs()[t]?.focus()),this.dispatchEvent(new CustomEvent("w1c-tab-change",{bubbles:!0,composed:!0,detail:{selected:t}}))}getTabs(){return this.tabsSlot?.assignedElements({flatten:!0})??[]}getPanels(){return this.panelsSlot?.assignedElements({flatten:!0})??[]}isDisabled(t){return t.hasAttribute("disabled")||t.getAttribute("aria-disabled")==="true"}getNextEnabledTabIndex(t,e){let o=this.getTabs();for(let a=1;a<=o.length;a+=1){let r=(t+a*e+o.length)%o.length;if(!this.isDisabled(o[r]))return r}return this.selected}},Yt.styles=h`
		:host {
			display: block;
			color: var(--w1c-tabs-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			min-width: 0;
		}

		.tablist {
			display: flex;
			align-items: end;
			gap: var(--w1c-tabs-gap, 1px);
			padding-inline: var(--w1c-tabs-tablist-padding-inline, var(--w1c-space-1, 4px));
		}

		.tablist ::slotted(*) {
			box-sizing: border-box;
			min-height: var(--w1c-tab-height, 24px);
			padding: var(--w1c-tab-padding, 3px 10px);
			border: var(--w1c-tab-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-tab-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-tab-highlight, var(--w1c-control-highlight, #ffffff));
			border-block-end: 0;
			border-radius: var(--w1c-tab-radius, var(--w1c-radius-1, 0) var(--w1c-radius-1, 0) 0 0);
			color: var(--w1c-tab-text, var(--w1c-control-text, #111111));
			background: var(--w1c-tab-background, var(--w1c-surface, #c0c0c0));
			font: var(--w1c-control-font, inherit);
			text-decoration: none;
			cursor: default;
		}

		.tablist ::slotted([aria-selected='true']) {
			position: relative;
			z-index: 1;
			padding-block-end: calc(var(--w1c-tab-padding-block-end-active, 3px) + 1px);
			color: var(--w1c-tab-active-text, var(--w1c-tab-text, var(--w1c-control-text, #111111)));
			background: var(--w1c-tab-active-background, var(--w1c-window-content-background, #ffffff));
		}

		.panels {
			box-sizing: border-box;
			min-width: 0;
			padding: var(--w1c-tabs-panel-padding, var(--w1c-space-3, 12px));
			border: var(--w1c-tabs-panel-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-tabs-panel-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-tabs-panel-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-tabs-panel-background, var(--w1c-window-content-background, #ffffff));
		}
	`,Yt);sr([c({type:Number,reflect:!0})],Zt.prototype,"selected",void 0);sr([S('slot[name="tabs"]')],Zt.prototype,"tabsSlot",void 0);sr([S("slot:not([name])")],Zt.prototype,"panelsSlot",void 0);Zt=sr([p("w1c-tabs")],Zt)});var qa,Qt,Dr,ia=f(()=>{v();w();qa=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},Dr=(Qt=class extends d{render(){return l`
			<nav part="chrome" class="chrome" aria-label="Taskbar">
				<div part="start" class="start"><slot name="start"></slot></div>
				<div part="content" class="content"><slot></slot></div>
				<div part="tray" class="tray"><slot name="tray"></slot></div>
			</nav>
		`}},Qt.styles=h`
		:host {
			display: block;
			color: var(--w1c-taskbar-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			min-height: var(--w1c-taskbar-height, 30px);
			display: grid;
			grid-template-columns: auto minmax(0, 1fr) auto;
			align-items: center;
			gap: var(--w1c-taskbar-gap, var(--w1c-space-1, 4px));
			padding: var(--w1c-taskbar-padding, 3px 4px);
			border-block-start: var(--w1c-taskbar-border-block-start, 1px solid var(--w1c-control-highlight, #ffffff));
			border-block-end: var(--w1c-taskbar-border-block-end, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-taskbar-background, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-taskbar-shadow, none);
		}

		.start,
		.content,
		.tray {
			min-width: 0;
			display: flex;
			align-items: center;
			gap: var(--w1c-taskbar-gap, var(--w1c-space-1, 4px));
		}

		.content {
			overflow: hidden;
		}

		.tray {
			justify-content: end;
			padding-inline-start: var(--w1c-taskbar-tray-padding, var(--w1c-space-1, 4px));
			border-inline-start: var(--w1c-taskbar-tray-border, 1px solid var(--w1c-control-shadow, #808080));
		}

		.chrome ::slotted(w1c-button) {
			--w1c-button-background: var(--w1c-taskbar-button-background, var(--w1c-control-background, #c0c0c0));
			--w1c-button-active-background: var(
				--w1c-taskbar-button-active-background,
				var(--w1c-button-background, var(--w1c-control-background, #c0c0c0))
			);
			--w1c-button-text: var(--w1c-taskbar-button-text, var(--w1c-control-text, #111111));
			--w1c-button-radius: var(--w1c-taskbar-button-radius, var(--w1c-radius-1, 0));
			--w1c-button-padding: var(--w1c-taskbar-button-padding, 2px 10px);
		}
	`,Qt);Dr=qa([p("w1c-taskbar")],Dr)});var R,te,C,na=f(()=>{v();w();R=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},C=(te=class extends d{constructor(){super(...arguments),this.name="",this.value="",this.placeholder="",this.rows=4,this.disabled=!1,this.readonly=!1,this.required=!1,this.invalid=!1}focus(t){this.textarea?.focus(t)}render(){return l`
			<textarea
				part="control textarea"
				.name=${this.name}
				.value=${this.value}
				placeholder=${this.placeholder}
				rows=${this.rows}
				?disabled=${this.disabled}
				?readonly=${this.readonly}
				?required=${this.required}
				aria-invalid=${this.invalid?"true":"false"}
				@input=${this.handleInput}
				@change=${this.handleChange}></textarea>
		`}handleInput(t){this.value=t.currentTarget.value,this.dispatchEvent(new Event("input",{bubbles:!0,composed:!0}))}handleChange(){this.dispatchEvent(new Event("change",{bubbles:!0,composed:!0}))}},te.styles=h`
		:host {
			display: inline-block;
			min-width: min(100%, 220px);
			color: var(--w1c-textarea-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		textarea {
			box-sizing: border-box;
			width: 100%;
			min-height: var(--w1c-textarea-min-height, 72px);
			padding: var(--w1c-textarea-padding, 5px);
			border: var(--w1c-textarea-border, 1px solid var(--w1c-control-shadow, #808080));
			border-block-end-color: var(--w1c-textarea-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-end-color: var(--w1c-textarea-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-textarea-radius, var(--w1c-radius-1, 0));
			color: inherit;
			background: var(--w1c-textarea-background, var(--w1c-window-content-background, #ffffff));
			box-shadow: var(
				--w1c-textarea-shadow,
				inset 1px 1px 0 var(--w1c-control-dark-shadow, #404040),
				inset -1px -1px 0 var(--w1c-control-highlight, #ffffff)
			);
			font: inherit;
			resize: var(--w1c-textarea-resize, vertical);
		}

		textarea:focus-visible {
			outline: var(--w1c-textarea-focus-outline, 1px dotted var(--w1c-focus-ring, #000000));
			outline-offset: -3px;
		}

		textarea::placeholder {
			color: var(--w1c-textarea-placeholder, var(--w1c-disabled-text, #808080));
		}

		:host([invalid]) textarea {
			border-color: var(--w1c-textarea-invalid-border, var(--w1c-danger-text, #990000));
		}

		:host([disabled]) {
			color: var(--w1c-disabled-text, #808080);
		}
	`,te);R([c()],C.prototype,"name",void 0);R([c()],C.prototype,"value",void 0);R([c()],C.prototype,"placeholder",void 0);R([c({type:Number})],C.prototype,"rows",void 0);R([c({type:Boolean,reflect:!0})],C.prototype,"disabled",void 0);R([c({type:Boolean,reflect:!0})],C.prototype,"readonly",void 0);R([c({type:Boolean,reflect:!0})],C.prototype,"required",void 0);R([c({type:Boolean,reflect:!0})],C.prototype,"invalid",void 0);R([S("textarea")],C.prototype,"textarea",void 0);C=R([p("w1c-textarea")],C)});var je,ee,rt,sa=f(()=>{v();w();qe();je=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},rt=(ee=class extends d{constructor(){super(...arguments),this.open=!0,this.title="",this.variant="status",this.closeable=!1}render(){return l`
			<aside
				part="chrome"
				class="chrome"
				role=${this.variant==="danger"||this.variant==="warning"?"alert":"status"}
				aria-hidden=${this.open?"false":"true"}
				?hidden=${!this.open}>
				<span part="icon" class="icon"><slot name="icon"></slot></span>
				<div part="content" class="content">
					<strong part="title" class="title" ?hidden=${!this.title}>${this.title}</strong>
					<slot></slot>
				</div>
				<div part="actions" class="actions"><slot name="actions"></slot></div>
				<w1c-button part="close" class="close" ?hidden=${!this.closeable} aria-label="Close" @click=${this.close}>
					x
				</w1c-button>
			</aside>
		`}close(){this.open=!1,this.dispatchEvent(new CustomEvent("w1c-toast-close",{bubbles:!0,composed:!0}))}},ee.styles=h`
		:host {
			display: block;
			width: min(var(--w1c-toast-width, 360px), 100%);
			color: var(--w1c-toast-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: auto minmax(0, 1fr) auto auto;
			align-items: start;
			gap: var(--w1c-toast-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-toast-padding, var(--w1c-space-3, 12px));
			border: var(--w1c-toast-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-toast-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-toast-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-toast-radius, var(--w1c-radius-1, 0));
			background: var(--w1c-toast-background, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-toast-shadow, var(--w1c-shadow-window, 2px 2px 0 rgb(0 0 0 / 0.35)));
		}

		:host([variant='info']) .chrome {
			border-inline-start-color: var(--w1c-toast-info, var(--w1c-color-blue-4, #064db0));
		}

		:host([variant='warning']) .chrome {
			border-inline-start-color: var(--w1c-toast-warning, var(--w1c-color-yellow-3, #8a6710));
		}

		:host([variant='danger']) .chrome {
			border-inline-start-color: var(--w1c-toast-danger, var(--w1c-color-red-3, #c33b2b));
		}

		.icon,
		.actions {
			display: inline-flex;
			align-items: center;
			min-width: 0;
		}

		.content {
			min-width: 0;
		}

		.title {
			display: block;
			margin-block-end: var(--w1c-space-1, 4px);
			font: var(
				--w1c-toast-title-font,
				var(
					--w1c-titlebar-font,
					700 var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
						var(--w1c-font-heading, 'MS Sans Serif', Tahoma, sans-serif)
				)
			);
		}

		.close {
			--w1c-button-padding: 1px 6px;
		}

		[hidden] {
			display: none;
		}
	`,ee);je([c({type:Boolean,reflect:!0})],rt.prototype,"open",void 0);je([c()],rt.prototype,"title",void 0);je([c({reflect:!0})],rt.prototype,"variant",void 0);je([c({type:Boolean,reflect:!0})],rt.prototype,"closeable",void 0);rt=je([p("w1c-toast")],rt)});var cr,re,oe,ca=f(()=>{v();w();cr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},oe=(re=class extends d{constructor(){super(...arguments),this.src="",this.color="",this.tileSize=""}render(){let t=[this.src?`--w1c-tiled-image: url("${this.src.replaceAll('"',"%22")}")`:"",this.color?`--w1c-tiled-color: ${this.color}`:"",this.tileSize?`--w1c-tiled-size: ${this.tileSize}`:""].filter(Boolean).join("; ");return l`
			<section part="chrome" class="chrome" style=${t}>
				<div part="content" class="content"><slot></slot></div>
			</section>
		`}},re.styles=h`
		:host {
			display: block;
			color: var(--w1c-tiled-text, var(--w1c-control-text, #000000));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			min-width: 0;
			min-height: var(--w1c-tiled-min-height, 160px);
			padding: var(--w1c-tiled-padding, var(--w1c-space-4, 16px));
			background-color: var(--w1c-tiled-color, #000066);
			background-image: var(--w1c-tiled-image, radial-gradient(circle at 2px 2px, #ffffff 1px, transparent 1.5px));
			background-repeat: repeat;
			background-size: var(--w1c-tiled-size, 16px 16px);
		}

		.content {
			box-sizing: border-box;
			min-width: 0;
		}
	`,re);cr([c()],oe.prototype,"src",void 0);cr([c()],oe.prototype,"color",void 0);cr([c({attribute:"tile-size"})],oe.prototype,"tileSize",void 0);oe=cr([p("w1c-tiled-background")],oe)});var la,ae,lr,da=f(()=>{v();w();la=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},lr=(ae=class extends d{constructor(){super(...arguments),this.message="Under Construction"}render(){return l`
			<section part="chrome" class="chrome" role="status" aria-label=${this.message}>
				<div part="sign" class="sign">
					<span part="icon" class="icon"><slot name="icon">!</slot></span>
					<strong part="message" class="message">${this.message}</strong>
				</div>
				<div part="details" class="details"><slot></slot></div>
			</section>
		`}},ae.styles=h`
		:host {
			display: block;
			color: var(--w1c-construction-text, #000000);
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			gap: var(--w1c-construction-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-construction-padding, var(--w1c-space-2, 8px));
			border: var(--w1c-construction-border, 3px ridge #ff9900);
			background: var(--w1c-construction-background, #ffffcc);
			text-align: center;
		}

		.sign {
			box-sizing: border-box;
			display: flex;
			align-items: center;
			justify-content: center;
			gap: var(--w1c-space-2, 8px);
			min-width: 0;
			padding: var(--w1c-construction-sign-padding, 8px);
			border: var(--w1c-construction-sign-border, 2px solid #000000);
			background: var(--w1c-construction-stripes, repeating-linear-gradient(45deg, #ffff00 0 10px, #000000 10px 20px));
		}

		.icon,
		.message {
			box-sizing: border-box;
			display: inline-grid;
			place-items: center;
			background: var(--w1c-construction-label-background, #ffffff);
			border: var(--w1c-construction-label-border, 2px outset #ff9900);
		}

		.icon {
			width: 24px;
			height: 24px;
			font-weight: 900;
		}

		.message {
			min-width: 0;
			padding: 3px 8px;
			font: var(--w1c-construction-message-font, 700 18px/1.1 var(--w1c-font-heading, cursive));
			text-transform: uppercase;
			overflow-wrap: anywhere;
		}

		.details {
			min-width: 0;
		}
	`,ae);la([c()],lr.prototype,"message",void 0);lr=la([p("w1c-under-construction")],lr)});var ha,ie,dr,pa=f(()=>{v();w();ha=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},dr=(ie=class extends d{constructor(){super(...arguments),this.variant="error"}render(){return l`
			<p
				part="chrome"
				class="chrome"
				role=${this.variant==="error"?"alert":"status"}
				data-variant=${this.variant}>
				<span part="icon" class="icon" aria-hidden="true"><slot name="icon">${this.defaultIcon}</slot></span>
				<span part="content" class="content"><slot></slot></span>
			</p>
		`}get defaultIcon(){return this.variant==="warning"?"!":this.variant==="info"?"i":"x"}},ie.styles=h`
		:host {
			display: block;
			color: var(--w1c-validation-message-text, var(--w1c-danger-text, #990000));
			font: var(
				--w1c-control-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-tight, 1.2)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			display: flex;
			align-items: flex-start;
			gap: var(--w1c-validation-message-gap, var(--w1c-space-1, 4px));
			margin: 0;
		}

		.icon {
			display: inline-grid;
			place-items: center;
			width: var(--w1c-validation-message-icon-size, 14px);
			height: var(--w1c-validation-message-icon-size, 14px);
			border: var(--w1c-validation-message-icon-border, 1px solid currentColor);
			border-radius: 50%;
			font-size: 10px;
			line-height: 1;
			text-transform: uppercase;
		}

		.chrome[data-variant='warning'] {
			color: var(--w1c-validation-message-warning-text, var(--w1c-warning-text, #6f4a00));
		}

		.chrome[data-variant='info'] {
			color: var(--w1c-validation-message-info-text, var(--w1c-info-text, #003c8f));
		}
	`,ie);ha([c({reflect:!0})],dr.prototype,"variant",void 0);dr=ha([p("w1c-validation-message")],dr)});var hr,ne,se,fa=f(()=>{v();w();hr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},se=(ne=class extends d{constructor(){super(...arguments),this.value="0",this.digits=6,this.label="Visitors"}render(){let t=String(this.value||"0").replace(/\D/g,"")||"0",e=t.padStart(Math.max(0,this.digits),"0");return l`
			<div part="chrome" class="chrome" role="group" aria-label=${`${this.label}: ${t}`}>
				<span part="label" class="label">${this.label}</span>
				<span part="digits" class="digits" aria-hidden="true">
					${e.split("").map(o=>l`<span part="digit" class="digit">${o}</span>`)}
				</span>
			</div>
		`}},ne.styles=h`
		:host {
			display: inline-block;
			color: var(--w1c-counter-text, #00ff66);
			font: var(--w1c-counter-font, 700 13px/1 var(--w1c-font-mono, 'Courier New', monospace));
		}

		.chrome {
			box-sizing: border-box;
			display: inline-grid;
			grid-template-columns: auto auto;
			align-items: center;
			gap: var(--w1c-counter-gap, 5px);
			padding: var(--w1c-counter-padding, 3px 5px);
			border: var(--w1c-counter-border, 2px inset #808080);
			background: var(--w1c-counter-background, #000000);
			box-shadow: var(--w1c-counter-shadow, 1px 1px 0 #ffffff);
		}

		.label {
			color: var(--w1c-counter-label-text, #ffff00);
			font: var(--w1c-counter-label-font, 700 10px/1 var(--w1c-font-ui, Arial, sans-serif));
			text-transform: uppercase;
		}

		.digits {
			display: inline-flex;
			gap: 1px;
		}

		.digit {
			box-sizing: border-box;
			display: grid;
			place-items: center;
			min-width: var(--w1c-counter-digit-width, 1.15em);
			padding: 1px 2px;
			border: var(--w1c-counter-digit-border, 1px solid #333333);
			background: var(--w1c-counter-digit-background, linear-gradient(#222222, #000000 45%, #151515 46%, #000000));
			color: inherit;
		}
	`,ne);hr([c()],se.prototype,"value",void 0);hr([c({type:Number})],se.prototype,"digits",void 0);hr([c()],se.prototype,"label",void 0);se=hr([p("w1c-visitor-counter")],se)});var ua,ce,pr,va=f(()=>{v();w();ua=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},pr=(ce=class extends d{constructor(){super(...arguments),this.name="Webring"}render(){return l`
			<nav part="chrome" class="chrome" aria-label=${this.name}>
				<strong part="title" class="title">${this.name}</strong>
				<div part="content" class="content"><slot></slot></div>
				<div part="nav" class="nav">
					<slot name="previous"><a href="#">Previous</a></slot>
					<slot name="home"><a href="#">Ring Home</a></slot>
					<slot name="random"><a href="#">Random</a></slot>
					<slot name="next"><a href="#">Next</a></slot>
				</div>
			</nav>
		`}},ce.styles=h`
		:host {
			display: block;
			color: var(--w1c-webring-text, var(--w1c-control-text, #000000));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 14px) / var(--w1c-line-normal, 1.25) var(--w1c-font-ui, Arial, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			gap: var(--w1c-webring-gap, var(--w1c-space-2, 8px));
			padding: var(--w1c-webring-padding, var(--w1c-space-3, 12px));
			border: var(--w1c-webring-border, 3px double #0000ee);
			background: var(--w1c-webring-background, #ffffcc);
			text-align: center;
		}

		.title {
			color: var(--w1c-webring-title-text, #660099);
			font: var(--w1c-webring-title-font, 700 17px/1.1 var(--w1c-font-heading, cursive));
			text-decoration: underline;
		}

		.content {
			min-width: 0;
		}

		.nav {
			display: flex;
			flex-wrap: wrap;
			justify-content: center;
			gap: var(--w1c-webring-nav-gap, var(--w1c-space-2, 8px));
		}

		::slotted(a),
		a {
			color: var(--w1c-webring-link, #0000ee);
			font-weight: 700;
		}

		::slotted(a:visited),
		a:visited {
			color: var(--w1c-webring-link-visited, #660099);
		}
	`,ce);ua([c()],pr.prototype,"name",void 0);pr=ua([p("w1c-webring")],pr)});function ma(i,t,e){return{pointerId:i,start:t,origin:e}}function ba(i,t){return{x:i.origin.x+t.x-i.start.x,y:i.origin.y+t.y-i.start.y}}function ga(i,t,e){return{pointerId:i,start:t,origin:e}}function xa(i,t,e={}){let o=i.origin.width+t.x-i.start.x,a=i.origin.height+t.y-i.start.y;return{width:wa(o,e.minWidth,e.maxWidth),height:wa(a,e.minHeight,e.maxHeight)}}function wa(i,t=Number.NEGATIVE_INFINITY,e=Number.POSITIVE_INFINITY){return Math.min(Math.max(i,t),e)}function fr(i){return{x:i.clientX,y:i.clientY}}function Ua(i){return i.button===0&&i.isPrimary!==!1}function Ir(i,t){return!!(i&&i.pointerId===t.pointerId)}function Vr(i,t=i.currentTarget){return!Ua(i)||!(t instanceof HTMLElement)?null:(t.setPointerCapture(i.pointerId),{session:{pointerId:i.pointerId,target:t},point:fr(i)})}function Br(i,t){return!i||i.pointerId!==t.pointerId?!1:(i.target.hasPointerCapture(t.pointerId)&&i.target.releasePointerCapture(t.pointerId),!0)}var ya=f(()=>{});var z,le,_,$a=f(()=>{v();v();w();ya();$t();Ge();_t();z=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},_=(le=class extends d{constructor(){super(...arguments),this.title="Window",this.movable=!1,this.resizable=!1,this.moving=!1,this.resizing=!1,this.x=0,this.y=0,this.width=null,this.height=null,this.minWidth=220,this.minHeight=160,this.maxWidth=null,this.maxHeight=null,this.dragSession=null,this.dragPointerSession=null,this.resizeSession=null,this.resizePointerSession=null}render(){return l`
			<section part="chrome" class="chrome" role="group" aria-label=${this.title} style=${this.geometryStyle()}>
				<slot name="titlebar">
					<w1c-titlebar
						part="titlebar"
						class=${this.movable?"move-handle":""}
						exportparts="chrome: titlebar-chrome, titlebar, icon, title, controls"
						.title=${this.title}
						@pointerdown=${this.startDrag}
						@pointermove=${this.moveDrag}
						@pointerup=${this.endDrag}
						@pointercancel=${this.endDrag}>
						<slot name="icon" slot="icon"></slot>
						<slot name="controls" slot="controls"></slot>
					</w1c-titlebar>
				</slot>
				<slot name="toolbar">
					<w1c-toolbar
						part="toolbar"
						exportparts="chrome: toolbar-chrome, toolbar, controls: toolbar-controls"></w1c-toolbar>
				</slot>
				<div part="content" class="content">
					<slot></slot>
				</div>
				<slot name="statusbar">
					<w1c-statusbar part="statusbar" exportparts="chrome: statusbar-chrome, statusbar, content: statusbar-content">
						Ready
					</w1c-statusbar>
				</slot>
				${this.resizable?l`
							<span
								part="resize-handle"
								class="resize-handle"
								role="separator"
								aria-label="Resize window"
								@pointerdown=${this.startResize}
								@pointermove=${this.moveResize}
								@pointerup=${this.endResize}
								@pointercancel=${this.endResize}></span>
						`:b}
			</section>
		`}geometryStyle(){let t=[`transform: translate(${this.numberValue(this.x)}px, ${this.numberValue(this.y)}px);`];return this.width!==null&&t.push(`width: ${this.numberValue(this.width)}px;`),this.height!==null&&t.push(`height: ${this.numberValue(this.height)}px;`),t.join(" ")}startDrag(t){if(!this.movable||this.hasInteractiveTarget(t))return;let e=Vr(t);e&&(this.dragPointerSession=e.session,this.dragSession=ma(t.pointerId,e.point,{x:this.numberValue(this.x),y:this.numberValue(this.y)}),this.moving=!0,this.dispatchGeometryEvent("w1c-window-move-start"))}moveDrag(t){if(!Ir(this.dragSession,t)||!this.dragSession)return;let e=ba(this.dragSession,fr(t));this.x=e.x,this.y=e.y,this.dispatchGeometryEvent("w1c-window-move")}endDrag(t){Br(this.dragPointerSession,t)&&(this.dragPointerSession=null,this.dragSession=null,this.moving=!1,this.dispatchGeometryEvent("w1c-window-move-end"))}startResize(t){let e=Vr(t);if(!e)return;let o=this.getBoundingClientRect();this.resizePointerSession=e.session,this.resizeSession=ga(t.pointerId,e.point,{width:this.width===null?o.width:this.numberValue(this.width,o.width),height:this.height===null?o.height:this.numberValue(this.height,o.height)}),this.resizing=!0,this.dispatchGeometryEvent("w1c-window-resize-start")}moveResize(t){if(!Ir(this.resizeSession,t)||!this.resizeSession)return;let e=xa(this.resizeSession,fr(t),{minWidth:this.numberValue(this.minWidth),minHeight:this.numberValue(this.minHeight),maxWidth:this.maxWidth===null?void 0:this.numberValue(this.maxWidth),maxHeight:this.maxHeight===null?void 0:this.numberValue(this.maxHeight)});this.width=e.width,this.height=e.height,this.dispatchGeometryEvent("w1c-window-resize")}endResize(t){Br(this.resizePointerSession,t)&&(this.resizePointerSession=null,this.resizeSession=null,this.resizing=!1,this.dispatchGeometryEvent("w1c-window-resize-end"))}hasInteractiveTarget(t){return t.composedPath().some(e=>e instanceof HTMLButtonElement||e instanceof HTMLAnchorElement||e instanceof HTMLInputElement||e instanceof HTMLSelectElement||e instanceof HTMLTextAreaElement||e instanceof HTMLElement&&e.isContentEditable)}dispatchGeometryEvent(t){this.dispatchEvent(new CustomEvent(t,{bubbles:!0,composed:!0,detail:{x:this.numberValue(this.x),y:this.numberValue(this.y),width:this.width===null?null:this.numberValue(this.width),height:this.height===null?null:this.numberValue(this.height)}}))}numberValue(t,e=0){let o=Number(t);return Number.isFinite(o)?o:e}},le.styles=h`
		:host {
			display: block;
			min-width: min(100%, 220px);
			color: var(--w1c-window-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		:host([moving]),
		:host([resizing]) {
			user-select: none;
		}

		:host([moving]) {
			cursor: move;
		}

		:host([resizing]) {
			cursor: nwse-resize;
		}

		.chrome {
			box-sizing: border-box;
			position: relative;
			display: grid;
			grid-template-rows: auto auto minmax(0, 1fr) auto;
			min-height: var(--w1c-window-min-height, 160px);
			border: var(
				--w1c-window-border,
				1px solid var(--w1c-window-dark-shadow, var(--w1c-control-dark-shadow, #404040))
			);
			border-block-start-color: var(--w1c-window-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-window-highlight, var(--w1c-control-highlight, #ffffff));
			border-radius: var(--w1c-window-radius, var(--w1c-radius-1, 0));
			background: var(--w1c-window-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(
				--w1c-window-shadow,
				inset -1px -1px 0 var(--w1c-window-shadow-color, var(--w1c-control-shadow, #808080)),
				inset 1px 1px 0 var(--w1c-window-highlight, var(--w1c-control-highlight, #ffffff)),
				var(--w1c-window-shadow-outer, var(--w1c-shadow-none, none))
			);
			overflow: hidden;
			touch-action: none;
			will-change: transform, width, height;
		}

		.move-handle {
			cursor: move;
		}

		.content {
			box-sizing: border-box;
			min-width: 0;
			min-height: 0;
			padding: var(--w1c-window-content-padding, 12px);
			border: var(
				--w1c-window-content-border,
				1px solid var(--w1c-window-shadow-color, var(--w1c-control-shadow, #808080))
			);
			background: var(--w1c-window-background, var(--w1c-window-content-background, #ffffff));
			overflow: auto;
		}

		.resize-handle {
			box-sizing: border-box;
			position: absolute;
			inset-inline-end: 0;
			inset-block-end: 0;
			inline-size: var(--w1c-window-resize-handle-size, 14px);
			block-size: var(--w1c-window-resize-handle-size, 14px);
			cursor: nwse-resize;
			touch-action: none;
			background:
				linear-gradient(
						135deg,
						transparent 0 48%,
						var(--w1c-window-shadow-color, var(--w1c-control-shadow, #808080)) 49% 53%,
						transparent 54%
					)
					right 2px bottom 2px / 8px 8px no-repeat,
				linear-gradient(
						135deg,
						transparent 0 48%,
						var(--w1c-window-dark-shadow, var(--w1c-control-dark-shadow, #404040)) 49% 53%,
						transparent 54%
					)
					right 5px bottom 2px / 8px 8px no-repeat;
		}
	`,le);z([c()],_.prototype,"title",void 0);z([c({type:Boolean,reflect:!0})],_.prototype,"movable",void 0);z([c({type:Boolean,reflect:!0})],_.prototype,"resizable",void 0);z([c({type:Boolean,reflect:!0})],_.prototype,"moving",void 0);z([c({type:Boolean,reflect:!0})],_.prototype,"resizing",void 0);z([c({type:Number,reflect:!0})],_.prototype,"x",void 0);z([c({type:Number,reflect:!0})],_.prototype,"y",void 0);z([c({type:Number})],_.prototype,"width",void 0);z([c({type:Number})],_.prototype,"height",void 0);z([c({type:Number,attribute:"min-width"})],_.prototype,"minWidth",void 0);z([c({type:Number,attribute:"min-height"})],_.prototype,"minHeight",void 0);z([c({type:Number,attribute:"max-width"})],_.prototype,"maxWidth",void 0);z([c({type:Number,attribute:"max-height"})],_.prototype,"maxHeight",void 0);_=z([p("w1c-window")],_)});var qr,de,He,ka=f(()=>{v();w();$t();_t();qr=function(i,t,e,o){var a=arguments.length,r=a<3?t:o===null?o=Object.getOwnPropertyDescriptor(t,e):o,n;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")r=Reflect.decorate(i,t,e,o);else for(var s=i.length-1;s>=0;s--)(n=i[s])&&(r=(a<3?n(r):a>3?n(t,e,r):n(t,e))||r);return a>3&&r&&Object.defineProperty(t,e,r),r},He=(de=class extends d{constructor(){super(...arguments),this.label="Word processor",this.showDetails=!1}render(){return l`
			<section part="chrome" class="chrome" role="group" aria-label=${this.label}>
				<slot name="toolbar">
					<w1c-toolbar
						part="toolbar"
						exportparts="chrome: toolbar-chrome, toolbar, controls: toolbar-controls"></w1c-toolbar>
				</slot>
				<div part="ruler" class="ruler">
					<slot name="ruler">${this.renderDefaultRuler()}</slot>
				</div>
				<div part="workspace" class="workspace">
					<article part="page" class="page">
						<slot></slot>
					</article>
					<aside part="details" class="details" ?hidden=${!this.showDetails}>
						<slot name="details"></slot>
					</aside>
				</div>
				<slot name="statusbar">
					<w1c-statusbar part="statusbar" exportparts="chrome: statusbar-chrome, statusbar, content: statusbar-content">
						Page 1
					</w1c-statusbar>
				</slot>
			</section>
		`}renderDefaultRuler(){return l`<span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span>`}},de.styles=h`
		:host {
			display: block;
			min-width: min(100%, 280px);
			color: var(--w1c-word-processor-text, var(--w1c-control-text, #111111));
			font: var(
				--w1c-body-font,
				var(--w1c-font-size-2, 13px) / var(--w1c-line-normal, 1.35)
					var(--w1c-font-ui, 'MS Sans Serif', Tahoma, sans-serif)
			);
		}

		.chrome {
			box-sizing: border-box;
			display: grid;
			grid-template-rows: auto auto minmax(0, 1fr) auto;
			min-height: var(--w1c-word-processor-min-height, 320px);
			border: var(--w1c-word-processor-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			border-block-start-color: var(--w1c-word-processor-highlight, var(--w1c-control-highlight, #ffffff));
			border-inline-start-color: var(--w1c-word-processor-highlight, var(--w1c-control-highlight, #ffffff));
			background: var(--w1c-word-processor-frame, var(--w1c-surface, #c0c0c0));
			box-shadow: var(--w1c-word-processor-shadow, var(--w1c-window-shadow, none));
			overflow: hidden;
		}

		.ruler {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: repeat(7, minmax(32px, 1fr));
			gap: 0;
			padding: var(--w1c-word-processor-ruler-padding, 2px 8px);
			border-block-start: var(--w1c-word-processor-ruler-highlight, 1px solid var(--w1c-control-highlight, #ffffff));
			border-block-end: var(--w1c-word-processor-ruler-border, 1px solid var(--w1c-control-shadow, #808080));
			background:
				linear-gradient(to right, var(--w1c-control-shadow, #808080) 1px, transparent 1px) 0 100% / 16px 5px repeat-x,
				var(--w1c-word-processor-ruler-background, var(--w1c-surface, #c0c0c0));
			color: var(--w1c-word-processor-ruler-text, var(--w1c-disabled-text, #808080));
			font-size: 11px;
		}

		.workspace {
			box-sizing: border-box;
			display: grid;
			grid-template-columns: minmax(0, 1fr) auto;
			gap: var(--w1c-word-processor-workspace-gap, var(--w1c-space-3, 12px));
			min-width: 0;
			min-height: 0;
			padding: var(--w1c-word-processor-workspace-padding, var(--w1c-space-4, 16px));
			overflow: auto;
			background: var(--w1c-word-processor-workspace-background, #808080);
		}

		.page {
			box-sizing: border-box;
			width: min(100%, var(--w1c-word-processor-page-width, 680px));
			min-height: var(--w1c-word-processor-page-min-height, 420px);
			margin-inline: auto;
			padding: var(--w1c-word-processor-page-padding, 36px 44px);
			border: var(--w1c-word-processor-page-border, 1px solid var(--w1c-control-dark-shadow, #404040));
			color: var(--w1c-word-processor-page-text, #111111);
			background: var(--w1c-word-processor-page-background, #ffffff);
			box-shadow: var(--w1c-word-processor-page-shadow, 3px 3px 0 rgb(0 0 0 / 0.3));
			font: var(--w1c-word-processor-page-font, 15px/1.55 Georgia, 'Times New Roman', serif);
		}

		.details {
			box-sizing: border-box;
			width: var(--w1c-word-processor-details-width, 220px);
			min-height: 0;
			padding: var(--w1c-word-processor-details-padding, var(--w1c-space-2, 8px));
			overflow: auto;
			border: var(--w1c-word-processor-details-border, 1px solid var(--w1c-control-shadow, #808080));
			background: var(--w1c-word-processor-details-background, var(--w1c-window-content-background, #ffffff));
		}

		[hidden] {
			display: none;
		}

		@media (max-width: 680px) {
			.workspace {
				grid-template-columns: 1fr;
			}

			.details {
				width: auto;
			}
		}
	`,de);qr([c()],He.prototype,"label",void 0);qr([c({type:Boolean,reflect:!0,attribute:"show-details"})],He.prototype,"showDetails",void 0);He=qr([p("w1c-word-processor")],He)});var _a=f(()=>{Ur();Ar();xo();yo();ko();qe();_o();So();zo();Eo();Ao();Co();Oo();Mo();To();Vo();Bo();qo();Uo();Fo();Go();Jo();Ko();Yo();Zo();Qo();ta();ea();ra();$t();oa();aa();ia();na();Ge();sa();_t();ca();da();pa();fa();va();$a();ka();Hr()});var Fa=Sa(()=>{_a()});Fa();})();
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
@lit/reactive-element/decorators/custom-element.js:
@lit/reactive-element/decorators/property.js:
@lit/reactive-element/decorators/state.js:
@lit/reactive-element/decorators/event-options.js:
@lit/reactive-element/decorators/base.js:
@lit/reactive-element/decorators/query.js:
@lit/reactive-element/decorators/query-all.js:
@lit/reactive-element/decorators/query-async.js:
@lit/reactive-element/decorators/query-assigned-nodes.js:
lit-html/directive.js:
lit-html/directives/unsafe-html.js:
lit-html/directives/unsafe-svg.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
