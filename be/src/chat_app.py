import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import psutil
import time
import signal
import sys

class ChatDatabase:
    def __init__(self, db_path="chat_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella per i thread di conversazione
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella per i messaggi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES threads (id)
            )
        ''')
        
        # Tabella per i profili assistente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assistant_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                system_message TEXT NOT NULL,
                template TEXT NOT NULL,
                model_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_thread(self, title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (title) VALUES (?)", (title,))
        thread_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return thread_id
    
    def get_threads(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at FROM threads ORDER BY updated_at DESC")
        threads = cursor.fetchall()
        conn.close()
        return threads
    
    def add_message(self, thread_id, role, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", 
                      (thread_id, role, content))
        # Aggiorna il timestamp del thread
        cursor.execute("UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (thread_id,))
        conn.commit()
        conn.close()
    
    def get_messages(self, thread_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, timestamp FROM messages WHERE thread_id = ? ORDER BY timestamp", 
                      (thread_id,))
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def save_profile(self, name, system_message, template, model_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO assistant_profiles 
                         (name, system_message, template, model_name) VALUES (?, ?, ?, ?)''',
                      (name, system_message, template, model_name))
        conn.commit()
        conn.close()
    
    def get_profiles(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, system_message, template, model_name FROM assistant_profiles")
        profiles = cursor.fetchall()
        conn.close()
        return profiles
    
    def delete_thread(self, thread_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        conn.commit()
        conn.close()
    
    def rename_thread(self, thread_id, new_title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE threads SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                      (new_title, thread_id))
        conn.commit()
        conn.close()

class SystemMonitor:
    def __init__(self):
        self.cpu_percent = 0.0
        self.memory_percent = 0.0
        self.memory_used_gb = 0.0
        self.memory_total_gb = 0.0
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
    
    def add_callback(self, callback):
        """Aggiungi callback da chiamare quando i dati si aggiornano"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Avvia il monitoraggio in background"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Ferma il monitoraggio"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Loop di monitoraggio che gira in background"""
        while self.is_monitoring:
            try:
                # Aggiorna dati CPU e memoria
                self.cpu_percent = psutil.cpu_percent(interval=0.1)
                
                memory = psutil.virtual_memory()
                self.memory_percent = memory.percent
                self.memory_used_gb = memory.used / (1024**3)  # Converti in GB
                self.memory_total_gb = memory.total / (1024**3)
                
                # Chiama tutti i callback registrati
                for callback in self.callbacks:
                    try:
                        callback(self.cpu_percent, self.memory_percent, 
                               self.memory_used_gb, self.memory_total_gb)
                    except:
                        pass  # Ignora errori nei callback
                
                time.sleep(2)  # Aggiorna ogni 2 secondi
            except:
                time.sleep(5)  # In caso di errore, aspetta di più
    
    def get_current_stats(self):
        """Ottieni le statistiche correnti"""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used_gb': self.memory_used_gb,
            'memory_total_gb': self.memory_total_gb
        }

class ChatMLTemplates:
    @staticmethod
    def get_templates():
        return {
            "ChatML": {
                "system": "<|im_start|>system\n{system_message}<|im_end|>\n",
                "user": "<|im_start|>user\n{content}<|im_end|>\n",
                "assistant": "<|im_start|>assistant\n{content}<|im_end|>\n",
                "assistant_start": "<|im_start|>assistant\n"
            },
            "Alpaca": {
                "system": "### System:\n{system_message}\n\n",
                "user": "### Human:\n{content}\n\n",
                "assistant": "### Assistant:\n{content}\n\n",
                "assistant_start": "### Assistant:\n"
            },
            "Vicuna": {
                "system": "SYSTEM: {system_message}\n",
                "user": "USER: {content}\n",
                "assistant": "ASSISTANT: {content}\n",
                "assistant_start": "ASSISTANT: "
            }
        }

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = None
        self.base_dir = Path(__file__).resolve().parent
        self.cache_dir = self.base_dir / "cache"
    
    def load_model(self, model_name, progress_callback=None):
        if self.model_name == model_name and self.model is not None:
            return True
        
        # Fix 2: Check for conditional imports that might fail
        try:
            from transformers import AutoTokenizer
            import torch
            print("AutoTokenizer imported successfully")
        except ImportError as e:
            print(f"Import error: {e}")
            # Handle the error appropriately

        try:
            # Libera memoria precedente se necessario
            if self.model is not None:
                del self.model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            if progress_callback:
                progress_callback("Caricamento tokenizer...")
                
            if not self.tokenizer:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(self.cache_dir))
            
            if progress_callback:
                progress_callback("Caricamento modello...")
            
            # Ottimizzazioni per ridurre l'uso di memoria
            model_kwargs = {
                'cache_dir': str(self.cache_dir),
                'low_cpu_mem_usage': True,  # Riduce l'uso di RAM durante il caricamento
            }
            
            # Configurazione per CPU/GPU con ottimizzazioni memoria
            if torch.cuda.is_available():
                model_kwargs.update({
                    'torch_dtype': torch.float16,  # Usa half precision
                    'device_map': 'auto'
                })
            else:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer

                # Option 1: Use torch.float16 for reduced memory (no quantization library needed)
                model_kwargs = {
                    'torch_dtype': torch.float16,  # Half precision
                    'device_map': 'auto',  # Automatic device mapping
                    'low_cpu_mem_usage': True,  # Reduce CPU memory usage during loading
                }

                # Option 2: If bitsandbytes is available, use BitsAndBytesConfig
                try:
                    from transformers import BitsAndBytesConfig
                    
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_threshold=6.0,
                    )
                    
                    model_kwargs = {
                        'torch_dtype': torch.float16,
                        'device_map': 'auto',
                        'low_cpu_mem_usage': True,
                        'revision': 'float16'  # se disponibile

                    }
                    print("Using 8-bit quantization with BitsAndBytesConfig")
                    
                except ImportError:
                    print("BitsAndBytes not available, using float16 instead")
                    model_kwargs = {
                        'torch_dtype': torch.float16,
                        'device_map': 'auto',
                        'low_cpu_mem_usage': True,
                    }

                # Option 3: CPU-only setup (no CUDA required)
                if not torch.cuda.is_available():
                    model_kwargs = {
                        'torch_dtype': torch.float32,  # Use float32 for CPU
                        'device_map': 'cpu',
                        'low_cpu_mem_usage': True,
                    }
                    print("Using CPU-only configuration")

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                **model_kwargs
            )
            
            self.model_name = model_name
            
            if progress_callback:
                progress_callback("Modello caricato con successo!")
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Errore: {str(e)}")
            return False
    
    def generate_response(self, prompt, max_length=512, temperature=0.7, top_p=0.95, top_k=50):
        if not self.model or not self.tokenizer:
            return "Modello non caricato"
        
        try:
            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).input_ids
            
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_new_tokens=max_length,  # Usa max_new_tokens invece di max_length
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,  # Usa la cache per velocizzare
                )
            
            # Decodifica solo la nuova parte generata
            new_tokens = output[0][len(input_ids[0]):]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            return f"Errore nella generazione: {str(e)}"
    
    def cleanup(self):
        """Pulisce la memoria occupata dal modello"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

class ChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat con AI - ChatML Support")
        self.root.geometry("1200x800")
        
        self.db = ChatDatabase()
        self.model_manager = ModelManager()
        self.system_monitor = SystemMonitor()
        self.current_thread_id = None
        self.templates = ChatMLTemplates.get_templates()  # Corretto il nome della classe
        self.is_closing = False
        
        # Setup signal handlers per gestire Ctrl+C
        self.setup_signal_handlers()
        
        self.setup_ui()
        self.load_threads()
        self.load_profiles()
        self.start_system_monitoring()
    
    def setup_signal_handlers(self):
        """Configura i gestori di segnale per chiusura pulita"""
        def signal_handler(signum, frame):
            print("\nRicevuto segnale di interruzione, chiusura in corso...")
            self.cleanup_and_exit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup_and_exit(self):
        """Pulizia e chiusura dell'applicazione"""
        if self.is_closing:
            return
        
        self.is_closing = True
        print("Cleanup in corso...")
        
        # Ferma il monitoraggio sistema
        self.system_monitor.stop_monitoring()
        
        # Pulisci il modello
        self.model_manager.cleanup()
        
        # Chiudi la finestra
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        sys.exit(0)
    
    def setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame sinistro per thread e configurazioni
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Frame destro per la chat
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        # Notebook per le tab
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab Thread
        thread_frame = ttk.Frame(self.notebook)
        self.notebook.add(thread_frame, text="Thread")
        
        # Pulsanti thread
        thread_buttons = ttk.Frame(thread_frame)
        thread_buttons.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(thread_buttons, text="Nuovo Thread", 
                  command=self.new_thread).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(thread_buttons, text="Rinomina", 
                  command=self.rename_thread).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(thread_buttons, text="Elimina", 
                  command=self.delete_thread).pack(side=tk.LEFT)
        
        # Lista thread
        self.thread_listbox = tk.Listbox(thread_frame)
        self.thread_listbox.pack(fill=tk.BOTH, expand=True)
        self.thread_listbox.bind('<<ListboxSelect>>', self.on_thread_select)
        
        # Tab Configurazioni
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Config")
        
        # Configurazione modello
        ttk.Label(config_frame, text="Modello:").pack(anchor=tk.W)
        self.model_var = tk.StringVar(value="jan-hq/stealth-v1.2")  # Modello più piccolo di default
        model_entry = ttk.Entry(config_frame, textvariable=self.model_var, width=40)
        model_entry.pack(fill=tk.X, pady=(0, 10))
        
        model_buttons = ttk.Frame(config_frame)
        model_buttons.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(model_buttons, text="Carica Modello", 
                  command=self.load_model).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(model_buttons, text="Scarica Modello", 
                  command=self.unload_model).pack(side=tk.LEFT)
        
        # Template
        ttk.Label(config_frame, text="Template:").pack(anchor=tk.W)
        self.template_var = tk.StringVar(value="ChatML")
        template_combo = ttk.Combobox(config_frame, textvariable=self.template_var,
                                     values=list(self.templates.keys()), state="readonly")
        template_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Sistema
        ttk.Label(config_frame, text="Sistema:").pack(anchor=tk.W)
        self.system_text = scrolledtext.ScrolledText(config_frame, height=8, width=40)
        self.system_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.system_text.insert(tk.END, "Sei la Dea Astarte Syriaca, una divinità antica e saggia.")
        
        # Profili
        profile_frame = ttk.Frame(config_frame)
        profile_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(profile_frame, text="Profilo:").pack(anchor=tk.W)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var)
        self.profile_combo.pack(fill=tk.X, pady=(0, 5))
        self.profile_combo.bind('<<ComboboxSelected>>', self.load_profile)
        
        profile_buttons = ttk.Frame(profile_frame)
        profile_buttons.pack(fill=tk.X)
        ttk.Button(profile_buttons, text="Salva Profilo", 
                  command=self.save_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(profile_buttons, text="Carica", 
                  command=self.load_profile).pack(side=tk.LEFT)
    
    def setup_right_panel(self, parent):
        # Area chat
        self.chat_area = scrolledtext.ScrolledText(parent, state=tk.DISABLED, 
                                                  wrap=tk.WORD, height=30)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame input
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X)
        
        # Entry messaggio
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(input_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Pulsante invio
        ttk.Button(input_frame, text="Invia", 
                  command=self.send_message).pack(side=tk.RIGHT)
        
        # Status bar con frame per multiple sezioni
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status principale (sinistra)
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Monitor sistema (destra)
        self.system_status_var = tk.StringVar(value="CPU: --% | RAM: --% | --GB")
        self.system_status_bar = ttk.Label(status_frame, textvariable=self.system_status_var,
                                          relief=tk.SUNKEN, anchor=tk.E, width=25)
        self.system_status_bar.pack(side=tk.RIGHT)
    
    def unload_model(self):
        """Scarica il modello dalla memoria"""
        if messagebox.askyesno("Conferma", "Scaricare il modello dalla memoria?"):
            self.model_manager.cleanup()
            self.status_var.set("Modello scaricato dalla memoria")
    
    def load_threads(self):
        self.thread_listbox.delete(0, tk.END)
        threads = self.db.get_threads()
        for thread_id, title, created_at in threads:
            self.thread_listbox.insert(tk.END, f"{title} ({created_at[:16]})")
            self.thread_listbox.insert(tk.END, thread_id)  # Store ID
    
    def load_profiles(self):
        profiles = self.db.get_profiles()
        profile_names = [profile[0] for profile in profiles]
        self.profile_combo['values'] = profile_names
    
    def new_thread(self):
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        thread_id = self.db.create_thread(title)
        self.load_threads()
        self.current_thread_id = thread_id
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def delete_thread(self):
        selection = self.thread_listbox.curselection()
        if selection:
            # L'ID è memorizzato nella riga successiva
            thread_id = self.thread_listbox.get(selection[0] + 1)
            if messagebox.askyesno("Conferma", "Eliminare questo thread?"):
                self.db.delete_thread(thread_id)
                self.load_threads()
                if self.current_thread_id == thread_id:
                    self.current_thread_id = None
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.delete(1.0, tk.END)
                    self.chat_area.config(state=tk.DISABLED)
    
    def rename_thread(self):
        selection = self.thread_listbox.curselection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona un thread da rinominare")
            return
        
        # Ottieni il titolo attuale e l'ID
        current_title = self.thread_listbox.get(selection[0])
        # Rimuovi la data dal titolo per mostrare solo il nome
        current_name = current_title.split(" (")[0]
        thread_id = self.thread_listbox.get(selection[0] + 1)
        
        # Crea finestra di dialogo per il nuovo nome
        dialog = RenameDialog(self.root, "Rinomina Thread", current_name)
        new_name = dialog.result
        
        if new_name and new_name.strip():
            self.db.rename_thread(thread_id, new_name.strip())
            self.load_threads()
            # Riseleziona il thread rinominato
            self.select_thread_by_id(thread_id)
    
    def on_thread_select(self, event):
        selection = self.thread_listbox.curselection()
        if selection:
            # L'ID è memorizzato nella riga successiva
            thread_id = self.thread_listbox.get(selection[0] + 1)
            self.current_thread_id = thread_id
            self.load_conversation()
    
    def load_conversation(self):
        if not self.current_thread_id:
            return
        
        messages = self.db.get_messages(self.current_thread_id)
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        
        for role, content, timestamp in messages:
            self.display_message(role, content, timestamp)
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def display_message(self, role, content, timestamp=None):
        self.chat_area.config(state=tk.NORMAL)
        
        if timestamp:
            time_str = timestamp[:19]  # YYYY-MM-DD HH:MM:SS
        else:
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Formattazione del messaggio
        if role == "user":
            self.chat_area.insert(tk.END, f"[{time_str}] Tu: ", "user_label")
        elif role == "assistant":
            self.chat_area.insert(tk.END, f"[{time_str}] AI: ", "ai_label")
        elif role == "system":
            self.chat_area.insert(tk.END, f"[{time_str}] Sistema: ", "system_label")
        
        self.chat_area.insert(tk.END, f"{content}\n\n")
        
        # Configurazione tag per colori
        self.chat_area.tag_config("user_label", foreground="blue")
        self.chat_area.tag_config("ai_label", foreground="green")
        self.chat_area.tag_config("system_label", foreground="red")
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def format_conversation_with_template(self, messages, template_name):
        template = self.templates[template_name]
        formatted = ""
        
        for msg in messages:
            if msg["role"] == "system":
                formatted += template["system"].format(system_message=msg["content"])
            elif msg["role"] == "user":
                formatted += template["user"].format(content=msg["content"])
            elif msg["role"] == "assistant":
                formatted += template["assistant"].format(content=msg["content"])
        
        # Aggiungi il prompt per l'assistente
        formatted += template["assistant_start"]
        return formatted
    
    def send_message(self, event=None):
        message = self.message_var.get().strip()
        if not message:
            return
        
        if not self.current_thread_id:
            self.new_thread()
        
        # Aggiungi messaggio utente
        self.db.add_message(self.current_thread_id, "user", message)
        self.display_message("user", message)
        self.message_var.set("")
        
        # Genera risposta in thread separato
        threading.Thread(target=self.generate_response, daemon=True).start()
    
    def generate_response(self):
        try:
            self.status_var.set("Generando risposta...")
            
            # Ottieni tutti i messaggi del thread
            messages = self.db.get_messages(self.current_thread_id)
            
            # Converti in formato per il template
            conversation = []
            
            # Aggiungi sistema se presente
            system_msg = self.system_text.get(1.0, tk.END).strip()
            if system_msg:
                conversation.append({"role": "system", "content": system_msg})
            
            # Aggiungi messaggi della conversazione
            for role, content, _ in messages:
                conversation.append({"role": role, "content": content})
            
            # Formatta con template
            prompt = self.format_conversation_with_template(conversation, self.template_var.get())
            
            # Genera risposta
            response = self.model_manager.generate_response(prompt)
            
            # Aggiungi risposta al database e visualizza
            self.db.add_message(self.current_thread_id, "assistant", response)
            self.root.after(0, lambda: self.display_message("assistant", response))
            self.root.after(0, lambda: self.status_var.set("Pronto"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Errore: {str(e)}"))
    
    def load_model(self):
        model_name = self.model_var.get().strip()
        if not model_name:
            messagebox.showerror("Errore", "Inserire il nome del modello")
            return
        
        def progress_update(message):
            self.root.after(0, lambda: self.status_var.set(message))
        
        def load_in_thread():
            success = self.model_manager.load_model(model_name, progress_update)
            if not success:
                self.root.after(0, lambda: messagebox.showerror("Errore", "Impossibile caricare il modello"))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def save_profile(self):
        name = self.profile_var.get().strip()
        if not name:
            name = f"Profilo {datetime.now().strftime('%Y%m%d_%H%M')}"
        
        system_msg = self.system_text.get(1.0, tk.END).strip()
        template = self.template_var.get()
        model = self.model_var.get()
        
        self.db.save_profile(name, system_msg, template, model)
        self.load_profiles()
        messagebox.showinfo("Successo", f"Profilo '{name}' salvato!")
    
    def load_profile(self, event=None):
        profile_name = self.profile_var.get()
        if not profile_name:
            return
        
        profiles = self.db.get_profiles()
        for name, system_msg, template, model in profiles:
            if name == profile_name:
                self.system_text.delete(1.0, tk.END)
                self.system_text.insert(1.0, system_msg)
                self.template_var.set(template)
                self.model_var.set(model)
                break
    
    def start_system_monitoring(self):
        """Avvia il monitoraggio del sistema"""
        # Registra callback per aggiornare la status bar
        self.system_monitor.add_callback(self.update_system_status)
        self.system_monitor.start_monitoring()
    
    def update_system_status(self, cpu_percent, memory_percent, memory_used_gb, memory_total_gb):
        """Callback chiamato dal monitor del sistema per aggiornare la status bar"""
        try:
            # Formatta i dati con colori in base all'utilizzo
            cpu_color = self.get_usage_color(cpu_percent)
            mem_color = self.get_usage_color(memory_percent)
            
            status_text = f"CPU: {cpu_percent:.1f}% | RAM: {memory_percent:.1f}% | {memory_used_gb:.1f}/{memory_total_gb:.1f}GB"
            
            # Aggiorna la UI nel thread principale
            self.root.after(0, lambda: self.system_status_var.set(status_text))
            
            # Cambia colore della label in base all'utilizzo più alto
            max_usage = max(cpu_percent, memory_percent)
            color = self.get_usage_color(max_usage)
            self.root.after(0, lambda: self.system_status_bar.configure(foreground=color))
            
        except Exception as e:
            pass  # Ignora errori nell'aggiornamento UI
    
    def get_usage_color(self, percentage):
        """Restituisce il colore in base alla percentuale di utilizzo"""
        if percentage < 50:
            return "green"
        elif percentage < 80:
            return "orange"
        else:
            return "red"
    
    def select_thread_by_id(self, thread_id):
        """Seleziona un thread specifico nella lista dopo averla ricaricata"""
        for i in range(0, self.thread_listbox.size(), 2):  # Step 2 perché abbiamo titolo e ID
            if self.thread_listbox.get(i + 1) == str(thread_id):
                self.thread_listbox.selection_clear(0, tk.END)
                self.thread_listbox.selection_set(i)
                self.thread_listbox.activate(i)
                break

class RenameDialog:
    def __init__(self, parent, title, initial_value):
        self.result = None
        
        # Crea finestra di dialogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centra la finestra
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Frame principale
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(main_frame, text="Nuovo nome del thread:").pack(anchor=tk.W, pady=(0, 10))
        
        # Entry
        self.entry_var = tk.StringVar(value=initial_value)
        self.entry = ttk.Entry(main_frame, textvariable=self.entry_var, width=50)
        self.entry.pack(fill=tk.X, pady=(0, 20))
        self.entry.focus()
        self.entry.select_range(0, tk.END)
        
        # Frame pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Annulla", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", 
                  command=self.ok).pack(side=tk.RIGHT)
        
        # Bind eventi
        self.entry.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Aspetta che la finestra venga chiusa
        self.dialog.wait_window()
    
    def ok(self):
        self.result = self.entry_var.get()
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()

def main():
    root = tk.Tk()
    app = ChatApplication(root)
    
    # Gestisci chiusura pulita
    def on_closing():
        app.system_monitor.stop_monitoring()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()