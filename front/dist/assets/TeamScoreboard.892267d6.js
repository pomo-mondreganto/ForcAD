import{S as f}from"./Statuses.168e396a.js";import{g as k}from"./table.11b612b7.js";import{n as m,T as c,f as b}from"./index.89f1e795.js";var y=function(){var t=this,i=t.$createElement,e=t._self._c||i;return t.error!==null?e("div",[t._v(" "+t._s(t.error)+" ")]):t.team!==null?e("div",{staticClass:"table"},[e("div",{staticClass:"row"},[e("div",{staticClass:"team"},[t._v("team")]),e("div",{staticClass:"score"},[t._v("score")]),e("div",{staticClass:"service-name"},t._l(t.tasks,function(r){var s=r.name;return e("div",{key:s,staticClass:"service-cell"},[t._v(" "+t._s(s)+" ")])}),0)]),e("div",t._l(t.states,function(r,s){return e("div",{key:s,staticClass:"row"},[e("div",{staticClass:"team"},[e("div",{staticClass:"team-name"},[t._v(" "+t._s(t.team.name)+" ")]),e("div",{staticClass:"ip"},[t._v(" "+t._s(t.team.ip)+" ")])]),e("div",{staticClass:"score"},[t._v(" "+t._s(r.score.toFixed(2))+" ")]),e("div",{staticClass:"service"},t._l(r.tasks,function(a,n){var o=a.sla,u=a.score,d=a.stolen,v=a.lost,p=a.message,h=a.status;return e("div",{key:n,staticClass:"service-cell",style:{fontSize:1-t.tasks.length/20+"em",backgroundColor:t.getTeamTaskBackground(h)}},[e("button",{staticClass:"info"},[e("i",{staticClass:"fas fa-info-circle"}),e("span",{staticClass:"tooltip"},[t._v(" "+t._s(p)+" ")])]),e("div",{staticClass:"sla"},[e("strong",[t._v("SLA")]),t._v(": "+t._s(o.toFixed(2))+"% ")]),e("div",{staticClass:"fp"},[e("strong",[t._v("FP")]),t._v(": "+t._s(u.toFixed(2))+" ")]),e("div",{staticClass:"flags"},[e("i",{staticClass:"fas fa-flag"}),t._v(" +"+t._s(d)+"/-"+t._s(v)+" ")])])}),0)])}),0)]):t._e()},C=[];const g={data:function(){return{error:null,team:null,teamId:null,tasks:null,round:0,by_task:[],getTeamTaskBackground:k}},created:async function(){this.teamId=this.$route.params.id;try{const{data:t}=await this.$http.get("/client/teams/"),{data:i}=await this.$http.get("/client/tasks/");let{data:e}=await this.$http.get(`/client/teams/${this.teamId}/`);this.team=t.filter(({id:s})=>s==this.teamId)[0],this.tasks=i.map(s=>new c(s)).sort(c.comp),this.round=e.reduce((s,{round:a})=>Math.max(s,a),0),this.$store.commit("setRound",this.round),e=e.map(s=>({id:Number(s.id),round:Number(s.round),task_id:Number(s.task_id),team_id:Number(s.team_id),status:s.status,stolen:s.stolen,lost:s.lost,score:Number(s.score),checks:Number(s.checks),checks_passed:Number(s.checks_passed),timestamp_secs:Number(s.timestamp.slice(0,s.timestamp.indexOf("-"))),timestamp_num:Number(s.timestamp.slice(s.timestamp.indexOf("-")+1)),message:s.message})),e=e.sort(({timestamp_secs:s,timestamp_num:a},{timestamp_secs:n,timestamp_num:o})=>s===n?o-a:n-s),e=e.map(s=>new b(s)),this.by_task={};for(const s of e){let a=s.taskId-1;this.by_task[a]||(this.by_task[a]=[]),this.by_task[a].push(s)}this.by_task=Object.values(this.by_task);let r=Math.min(...this.by_task.map(s=>s.length));this.states=[];for(let s=0;s<r;s+=1)this.states.push({tasks:this.by_task.map(a=>a[s]),score:this.by_task.map(a=>a[s]).reduce((a,{score:n,sla:o})=>a+n*o/100,0)})}catch{this.error="Can't connect to server"}}},_={};var $=m(g,y,C,!1,T,"765a1ef4",null,null);function T(t){for(let i in _)this[i]=_[i]}var S=function(){return $.exports}(),N=function(){var t=this,i=t.$createElement,e=t._self._c||i;return e("div",[e("statuses"),e("team-scoreboard")],1)},w=[];const F={components:{TeamScoreboard:S,Statuses:f}},l={};var I=m(F,N,w,!1,M,"5c3fbe90",null,null);function M(t){for(let i in l)this[i]=l[i]}var z=function(){return I.exports}();export{z as default};
