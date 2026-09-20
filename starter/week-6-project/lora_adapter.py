"""Small, honest adaptation adapters.

The default path is dependency-free so the exercise runs on a fresh clone.  When
PyTorch, Transformers and PEFT are installed, ``PEFTAdapter`` trains a real LoRA
classification head on a tiny subset of the local BANKING77 training split.  The
automatic path can fall back and records that fact; the explicit ``mode=peft``
path fails instead, so it cannot misrepresent a smoke run as LoRA.
"""
from __future__ import annotations
import os, re, collections, platform, time

def tokens(s): return re.findall(r"[a-z0-9]+",s.lower())

class HashedAdapter:
    """A measured offline adapter. It is not mislabeled as transformer LoRA."""
    def __init__(self, rank=8): self.rank=rank; self.weights={}; self.labels=[]
    def fit(self, rows):
        self.labels=sorted({r["label"] for r in rows}); self.weights={label:collections.Counter() for label in self.labels}
        for r in rows:
            for t in set(tokens(r["text"])): self.weights[r["label"]][t]+=1
    def predict(self,text):
        ts=set(tokens(text)); scores={l:sum(c[t] for t in ts) for l,c in self.weights.items()}
        return max(scores,key=scores.get) if scores and max(scores.values()) else (self.labels[0] if self.labels else "unknown")

    def score(self, text):
        ts=set(tokens(text)); return {l:sum(c[t] for t in ts) for l,c in self.weights.items()}


class PEFTAdapter:
    """A tiny real LoRA adapter around a local/Hugging Face classifier.

    The model name is configurable with ``WEEK6_MODEL_NAME``.  Training is kept
    intentionally small (``WEEK6_PEFT_TRAIN_LIMIT``, default 64) so learners can
    inspect the full pipeline on a laptop.  It is only considered successful once
    the model has trained and produced predictions; callers must catch failures.
    """
    def __init__(self, labels, model_name=None, epochs=1, quantized=False):
        self.labels=list(labels); self.model_name=model_name or os.getenv("WEEK6_MODEL_NAME", "hf-internal-testing/tiny-random-distilbert")
        self.epochs=epochs; self.quantized=quantized; self.tokenizer=None; self.model=None; self.device="cpu"; self.train_seconds=0.0

    def fit(self, rows):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
        from peft import LoraConfig, TaskType, get_peft_model
        started=time.perf_counter()
        label_to_id={x:i for i,x in enumerate(self.labels)}
        self.tokenizer=AutoTokenizer.from_pretrained(self.model_name)
        model_kwargs={"num_labels":len(self.labels), "ignore_mismatched_sizes":True}
        if self.quantized:
            if not torch.cuda.is_available(): raise RuntimeError("QLoRA requires a CUDA-capable GPU")
            from transformers import BitsAndBytesConfig
            model_kwargs["quantization_config"]=BitsAndBytesConfig(load_in_4bit=True)
            model_kwargs["device_map"]="auto"; self.device="cuda"
        self.model=AutoModelForSequenceClassification.from_pretrained(self.model_name, **model_kwargs)
        # DistilBERT and BERT expose q/k/v linear layers.  Select only modules
        # that exist so the same path works with the tiny test models.
        names={n.split(".")[-1] for n,_ in self.model.named_modules()}
        targets=[x for x in ("q_lin","v_lin","query","value") if x in names]
        if not targets: raise RuntimeError("no supported attention projection modules found")
        self.model=get_peft_model(self.model,LoraConfig(
            task_type=TaskType.SEQ_CLS, r=4, lora_alpha=8, lora_dropout=0.05,
            target_modules=targets, modules_to_save=["classifier","pre_classifier"]
        ))
        limit=int(os.getenv("WEEK6_PEFT_TRAIN_LIMIT","64")); rows=list(rows)[:limit]
        class TinyDataset(torch.utils.data.Dataset):
            def __init__(self, data, tok): self.data=data; self.tok=tok
            def __len__(self): return len(self.data)
            def __getitem__(self, i):
                r=self.data[i]; out=self.tok(r["text"], truncation=True, padding="max_length", max_length=64)
                out={k:torch.tensor(v) for k,v in out.items()}; out["labels"]=torch.tensor(label_to_id[r["label"]]); return out
        args=TrainingArguments(
            output_dir=os.path.join("reports","peft-tmp"), num_train_epochs=self.epochs,
            per_device_train_batch_size=8, learning_rate=5e-4, logging_steps=9999,
            save_strategy="no", report_to=[], disable_tqdm=True
        )
        Trainer(model=self.model,args=args,train_dataset=TinyDataset(rows,self.tokenizer)).train()
        self.model.eval(); self.train_seconds=time.perf_counter()-started
        return self

    def predict(self, text):
        import torch
        batch=self.tokenizer(text,return_tensors="pt",truncation=True,padding=True,max_length=64)
        with torch.no_grad(): out=self.model(**batch).logits
        return self.labels[int(out.argmax(-1).item())]

def peft_available():
    try:
        import torch, transformers, peft  # noqa: F401
        return True
    except Exception: return False


def runtime_metadata():
    """Record enough information to reproduce or audit a real adapter run."""
    info={"python":platform.python_version(),"platform":platform.platform()}
    try:
        import torch
        info.update({"torch":torch.__version__,"cuda_available":torch.cuda.is_available(),"cuda":torch.version.cuda,"device":torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"})
    except Exception: pass
    for name in ("transformers","peft","bitsandbytes"):
        try: info[name]=getattr(__import__(name),"__version__","installed")
        except Exception: info[name]=None
    return info

def train_adapter(rows, labels, mode="auto", quantized=False):
    """Return a trained adapter and honest execution metadata.

    ``mode=peft`` is deliberately strict: it raises instead of silently using
    the fallback, so the real-LoRA command is a meaningful completion route.
    """
    if mode not in ("auto","peft","fallback"): raise ValueError("mode must be auto, peft, or fallback")
    if mode != "fallback" and peft_available():
        try:
            adapter=PEFTAdapter(labels,quantized=quantized).fit(rows)
            return adapter,{"requested":"QLoRA" if quantized else "LoRA","executed":"transformers_peft_qlora" if quantized else "transformers_peft_lora","is_transformer_lora":True,
                            "model":adapter.model_name,"train_limit":int(os.getenv("WEEK6_PEFT_TRAIN_LIMIT","64")),
                            "train_seconds":round(adapter.train_seconds,3),"rank":4,"quantized_4bit":quantized,"runtime":runtime_metadata()}
        except Exception as exc:
            if mode == "peft": raise RuntimeError(f"real {'QLoRA' if quantized else 'LoRA'} run failed: {type(exc).__name__}: {exc}") from exc
            fallback=HashedAdapter(); fallback.fit(rows)
            return fallback,{"requested":"LoRA/QLoRA","executed":"offline_hashed_adapter","is_transformer_lora":False,
                            "fallback_reason":f"PEFT unavailable at runtime: {type(exc).__name__}: {exc}","rank":fallback.rank,"runtime":runtime_metadata()}
    if mode == "peft": raise RuntimeError("real LoRA requested but torch, transformers, and peft are not installed; run make install-lora")
    fallback=HashedAdapter(); fallback.fit(rows)
    return fallback,{"requested":"LoRA/QLoRA","executed":"offline_hashed_adapter","is_transformer_lora":False,
                     "fallback_reason":"offline fallback explicitly requested" if mode=="fallback" else "torch/transformers/peft are not installed","rank":fallback.rank,"runtime":runtime_metadata()}
