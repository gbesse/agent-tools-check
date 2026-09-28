#!/usr/bin/env python3
"""Check whether an LLM gateway preserves agent tools and task messages."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

TEXT={
 "en":{"pass":"PASS: agent tools and task messages survived the gateway.","fail":"FAIL: the gateway lost an agent capability.","tool":"Tool missing upstream: {value}","call":"Tool call not restored for the client: {value}","args":"Tool call arguments changed: {value}","encryption":"Plain tool arguments need encrypted_function_args: []: {value}","message":"Agent task message missing upstream: {value}","invalid":"Invalid trace: {value}"},
 "fr":{"pass":"OK : outils et tâches de l'agent conservés par la gateway.","fail":"ÉCHEC : la gateway a perdu une capacité de l'agent.","tool":"Outil absent côté fournisseur : {value}","call":"Appel d'outil non restitué au client : {value}","args":"Arguments de l'appel modifiés : {value}","encryption":"Les arguments en clair exigent encrypted_function_args: [] : {value}","message":"Tâche de l'agent absente côté fournisseur : {value}","invalid":"Trace invalide : {value}"},
 "es":{"pass":"OK: la gateway conservó las herramientas y tareas del agente.","fail":"FALLO: la gateway perdió una capacidad del agente.","tool":"Herramienta ausente en el proveedor: {value}","call":"Llamada no restituida al cliente: {value}","args":"Cambian los argumentos de la llamada: {value}","encryption":"Los argumentos en claro requieren encrypted_function_args: []: {value}","message":"Falta el mensaje de tarea en el proveedor: {value}","invalid":"Traza no válida: {value}"},
}

def items(value):
 if isinstance(value,list): return value
 if isinstance(value,dict): return [value]
 return []

def content_text(value):
 if isinstance(value,str): return value
 if isinstance(value,list): return " ".join(content_text(x) for x in value)
 if isinstance(value,dict): return content_text(value.get("text",value.get("content","")))
 return ""

def offered(request):
 for tool in items(request.get("tools",[])):
  if tool.get("type")=="namespace":
   for child in items(tool.get("tools",[])):
    if child.get("type")=="function": yield tool.get("name"),child.get("name")

def tool_names(request):
 result=set()
 for tool in items(request.get("tools",[])):
  if tool.get("type")=="function": result.add(tool.get("name"))
  if tool.get("type")=="namespace":
   for child in items(tool.get("tools",[])):
    result.add(f"{tool.get('name')}__{child.get('name')}")
 return result

def calls(response):
 return [x for x in items(response.get("output",[])) if isinstance(x,dict) and x.get("type")=="function_call"]

def parse_args(value):
 if isinstance(value,str):
  try: return json.loads(value)
  except json.JSONDecodeError: return value
 return value

def inspect(trace):
 for name in ("client_request","upstream_request","upstream_response","client_response"):
  if not isinstance(trace.get(name),dict): raise ValueError(f"{name} must be an object")
 client,upstream,model,returned=(trace[x] for x in ("client_request","upstream_request","upstream_response","client_response"))
 failures=[];names=tool_names(upstream)
 for namespace,name in offered(client):
  flat=f"{namespace}__{name}"
  if flat not in names: failures.append(("tool",flat))
 for call in calls(model):
  flat=call.get("name","")
  match=next(((n,k) for n,k in offered(client) if flat in (f"{n}__{k}",k)),None)
  if not match: continue
  namespace,name=match
  matches=[x for x in calls(returned) if x.get("name")==name and x.get("namespace")==namespace]
  if not matches: failures.append(("call",f"{namespace}.{name}"));continue
  returned_call=matches[0]
  if parse_args(returned_call.get("arguments"))!=parse_args(call.get("arguments")): failures.append(("args",f"{namespace}.{name}"))
  if returned_call.get("encrypted_function_args","MISSING")!=[]: failures.append(("encryption",f"{namespace}.{name}"))
 forwarded=" ".join(content_text(x) for x in items(upstream.get("messages",[]))+items(upstream.get("input",[])))
 for message in items(client.get("input",[])):
  if isinstance(message,dict) and message.get("type")=="agent_message":
   task=content_text(message.get("content",[])).strip()
   if task and task not in forwarded: failures.append(("message",task[:80]))
 return failures

def demo_trace(broken):
 t={"client_request":{"tools":[{"type":"namespace","name":"collaboration","tools":[{"type":"function","name":"spawn_agent"}]}],"input":[{"type":"agent_message","recipient":"/root/worker","content":[{"type":"input_text","text":"Reply PONG-W"}]}]},"upstream_request":{"tools":[{"type":"function","name":"collaboration__spawn_agent"}],"messages":[{"role":"user","content":"Reply PONG-W"}]},"upstream_response":{"output":[{"type":"function_call","name":"collaboration__spawn_agent","arguments":"{\"message\":\"Reply PONG-W\"}"}]},"client_response":{"output":[{"type":"function_call","name":"spawn_agent","namespace":"collaboration","arguments":"{\"message\":\"Reply PONG-W\"}","encrypted_function_args":[]}]}}
 if broken:
  t["upstream_request"]["tools"]=[]
  t["upstream_request"]["messages"]=[]
  t["client_response"]["output"][0].pop("namespace")
  t["client_response"]["output"][0].pop("encrypted_function_args")
 return t

def main(argv=None):
 p=argparse.ArgumentParser(description="Check an agent gateway trace for lost tools and task messages.")
 p.add_argument("action",choices=["demo","check"]);p.add_argument("trace",nargs="?")
 p.add_argument("--lang",choices=TEXT,default="en");p.add_argument("--json",action="store_true")
 a=p.parse_args(argv)
 if a.action=="check" and not a.trace: p.error("check requires a trace JSON file")
 if a.action=="demo":
  for label,trace in [("broken",demo_trace(True)),("fixed",demo_trace(False))]:
   failures=inspect(trace)
   print(f"{label}: {TEXT[a.lang]['pass' if not failures else 'fail']}")
   for code,value in failures: print("  "+TEXT[a.lang][code].format(value=value))
  return 0
 try:
  trace=json.loads(Path(a.trace).read_text())
  failures=inspect(trace)
 except (OSError,json.JSONDecodeError,ValueError) as exc:
  print(TEXT[a.lang]["invalid"].format(value=exc),file=sys.stderr);return 1
 if a.json: print(json.dumps({"ok":not failures,"failures":[{"code":x,"value":y} for x,y in failures]}))
 else:
  print(TEXT[a.lang]["pass" if not failures else "fail"])
  for code,value in failures: print("  "+TEXT[a.lang][code].format(value=value))
 return 0 if not failures else 2
if __name__=="__main__":raise SystemExit(main())
