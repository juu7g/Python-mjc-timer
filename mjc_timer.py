"""
複数ジョブ連続タイマー
Multiple job continuous timer
複数の時間設定
時間の設定はダイアログでタブに秒単位、分単位で事前定義
外部から呼び出し可能
"""
from logging import getLogger, StreamHandler, Formatter, DEBUG
logger = getLogger(__name__)

import tkinter as tk
from tkinter import ttk, messagebox
import winsound as ws
from collections import deque
from datetime import datetime, timedelta
import json, sys, os
sys.path.append(os.path.dirname(sys.executable))    # 実行時フォルダをパスに追加

class MyFrame(tk.Frame):
    """
    ビュークラス
    """
    def __init__(self, master) -> None:
        """
        コンストラクタ：画面作成
        """
        super().__init__(master)
        # 時間選択コンボボックス
        self.times = {'5秒':5, '10秒':10, '15秒':15, '20秒':20} # 仮の初期値
        self.var_time = tk.StringVar()
        self.cmb_time = ttk.Combobox(master, justify=tk.CENTER
                                    , textvariable=self.var_time
                                    , values=list(self.times.keys()))
        self.cmb_time.option_add('*TCombobox*Listbox.Justify', 'center')
        self.cmb_time.pack()
        self.cmb_time.set('5秒')
        # 開始ボタン
        self.btn_start = tk.Button(master, text='開始', command=lambda:self.my_ctr.countdown(self.times[self.var_time.get()]))
        self.btn_start.pack(fill=tk.X)
        # シーケンス選択コンボボックス
        self.var_seqs = tk.StringVar()
        self.cmb_seqs = ttk.Combobox(master, justify=tk.CENTER, textvariable=self.var_seqs)
        self.cmb_seqs.pack()
        # シーケンス開始ボタン
        self.btn_seq_start = tk.Button(master, text='シーケンス開始'
                            , command=lambda:self.my_ctr.seq_countdown())
        self.btn_seq_start.pack(fill=tk.X)
        # ジョブリストボックス
        self.var_jobs = tk.StringVar(value=[])
        self.lbx_jobs = tk.Listbox(master, listvariable=self.var_jobs, height=0)
        self.lbx_jobs.pack(fill=tk.X)
        # 残り時間表示
        self.lbl_rest = tk.Label(master, text=' ', bg='pink'
                        , font=('Meiryo UI', 50, 'bold'))
        self.lbl_rest.pack(fill=tk.BOTH)
        # 進捗表示
        self.lbl_counter = tk.Label(master, wraplength=130, height=6, anchor=tk.NW
                        , justify=tk.LEFT, relief=tk.RIDGE)
        self.lbl_counter.pack(fill=tk.BOTH, expand=True)
        # 説明表示
        self.lbl_explain = tk.Label(master
                        , font=('Meiryo UI', 20), text=' ', relief=tk.RIDGE)
        self.lbl_explain.pack(fill=tk.X)
        # 中断ボタン
        self.btn_break = tk.Button(master, text='中断'
                            , command=lambda:self.my_ctr.abort_cd())
        self.btn_break.pack(fill=tk.X)

    def set_wraplength(self):
        """
        説明用ラベルの折り返し幅をリストボックスの幅に合わせる
        """
        self.lbl_explain.config(wraplength=self.lbx_jobs.winfo_width())

    def set_my_ctr(self, my_ctr):
        """
        MyControlクラスの参照を設定
        Args:
            MyControl:  MyControlオブジェクト
        """
        self.my_ctr = my_ctr
        self.cmb_seqs.bind('<<ComboboxSelected>>', self.my_ctr.set_jobs)

    def update_count(self, count:int):
        """
        残り時間の表示更新
        ウィジェット変数を使って更新するとぎくしゃくするので
        使わずに複数のウィジェットに値を設定して最後にupdate_idletasks()する
        Args:
            int:    残り時間(秒)
        """
        m, s = divmod(count, 60)                    # 秒を分と秒に分ける
        if m == 0:  # 1分未満の場合
            self.lbl_rest['text'] = s
            self.lbl_counter.config(text='●'*s)
        else:
            self.lbl_rest['text'] = f"{m}:{s}"
            self.lbl_counter.config(text='◎'*m)
        self.update_idletasks()

class MyModel():
    """
    モデルクラス
    """
    def __init__(self) -> None:
        """
        コンストラクタ：JSONファイルの読み込み
        """
        try:
            # マルチジョブカウントダウンタイマーデータの読み込み
            path = "mjc_timer.json"
            with open(path, 'r') as f:
                self.mjc_json = json.load(f, object_hook=self.str_to_sec)
            # シンプルタイマーデータの読み込み
            path = "timer.json"
            with open(path, 'r') as f:
                self.timer_json = json.load(f, object_hook=self.str_to_sec)
        except FileNotFoundError:
            messagebox.showerror("エラー", f"ファイルが存在しません - {path}")
            sys.exit(1)
        except json.decoder.JSONDecodeError as e:
            messagebox.showerror("JSON記述エラー", f"{e.msg}")
            sys.exit(1)
        except Exception as e2:
            messagebox.showerror("例外", f"{e2.msg}")
            sys.exit(1)

    def to_sec(self, x) -> int:
        """
        文字で書かれた時間を秒に変更
        Args:
            any:    時間(秒を示すint、秒、分秒を示す文字列)
        Returns:
            int:    秒
        """
        # 整数の場合はそのまま返す。このケースが多いので先に判断する
        if isinstance(x, int): return x
        
        try:
            t = datetime.strptime(x, "%M:%S")
            t = int(timedelta(minutes=t.minute, seconds=t.second).total_seconds())
        except ValueError:
            t = int(x)
        return t

    def str_to_sec(self, d:dict) -> dict:
        """
        辞書を編集して辞書で返す(json.load()のpbject_hook用)
        時間の値にある文字を秒に変更
        辞書の構成：{ジョブキー:[[表示, 時間],[]...]
        Args:
            dict:   辞書
        Returns:
            dict:   変換後辞書
        """
        for k ,v in d.items():
            d[k] = [[kk, self.to_sec(vv)] for kk, vv in v]
        return d

class MyControl():
    """
    コントロールクラス
    """

    def __init__(self, model:MyModel, view:MyFrame) -> None:
        """
        コンストラクタ
        Args:
            MyModel:    モデルのオブジェクト
            MyFrame:    ビューのオブジェクト
        """
        self.model = model  # モデルオブジェクト
        self.view = view    # ビューオブジェクト
        # マルチジョブカウントダウンタイマーのデータをモデルからビューへ
        # シーケンスの取得(一層目がシーケンスの辞書)
        d = self.model.mjc_json
        self.view.cmb_seqs.config(values=list(d.keys()))
        job = list(d.keys())[0]     # 先頭を取得
        self.view.cmb_seqs.set(job) # 先頭を選択状態に
        self.set_jobs()             # ジョブをリストボックスに設定
        # シンプルタイマーのデータをモデルからビューへ(同じキーがあると後のものが残る)
        # シンプルタイマーのタプルのリストを取得(「シンプルタイマー」キーの値)
        d = dict((k, v) for k, v in self.model.timer_json["シンプルタイマー"])
        self.view.times = d # タイマー用辞書に設定
        self.view.cmb_time.config(values=list(d.keys())) # タイマー用コンボボックスにキーを設定
        job = list(d.keys())[0]     # 先頭を取得
        self.view.cmb_time.set(job) # 先頭を選択状態に

    def set_jobs(self, event=None):
        """
        選択されたシーケンスのジョブをリストボックスに設定
        """
        # モデルのデータをビューにセット
        d = self.model.mjc_json
        job = self.view.cmb_seqs.get()  # 選択されたシーケンスを取得
        # 選択されたシーケンスのタプルのリストを取得(「選択されたシーケンス」キーの値)
        # タプル：(内容, 時間)から「内容(分:秒)」に変換
        v = [f"{veiw} (%d:%02d)"%divmod(time, 60) for veiw, time in d[job]]
        self.view.var_jobs.set(v)       # リストボックスに設定

    def seq_countdown(self, event=None):
        """
        シーケンスのカウントダウン開始(先頭のジョブからカウントダウン開始)
        """
        self.view.set_wraplength()  # 説明用ラベルの折り返し幅をリストボックスの幅に合わせる
        # シーケンスの内容(ジョブ(内容と時間のタプルのリスト))をキューに設定
        self.que = deque(self.model.mjc_json[self.view.var_seqs.get()])
        # シーケンスの1件目の設定
        self.view.lbx_jobs.select_set(0)        # リストボックスの選択
        que = self.que.popleft()                # キューからデータ取得
        self.countdown(que[1])                  # カウントダウン開始
        self.view.lbl_explain["text"] = que[0]  # 説明を画面にセット
        logger.debug(f"シーケンス開始 {que[1]}")

    def countdown(self, count:int, event=None):
        """
        カウントダウン(1秒ごとに実行)次の実行をafter()メソッドで予約
        Args:
            int:    残り時間
        """
        # afterは速やかに処理して遅れを最小限にする
        if count > 0:
            # call countdown again after 1000ms (1s)
            self.after_id = self.view.after(1000, self.countdown, count - 1)
        else:
            # 次のジョブを設定
            try:
                que = self.que.popleft()                        # 次のシーケンスを取得
                # カウントダウン予約
                self.after_id = self.view.after(1000, self.countdown, que[1])
                self.view.lbl_explain["text"] = que[0]          # 説明を画面にセット
                # リストボックスの選択されている要素の選択を解除して次の要素を選択
                i = self.view.lbx_jobs.curselection()[0]        # 選択されているリストid取得
                self.view.lbx_jobs.select_clear(i)              # 選択解除
                self.view.lbx_jobs.select_set(i + 1)            # 選択設定
            except (IndexError, AttributeError) as e:
                # キューの残りがなくなった時の処理
                # リストボックスの選択状態を解除
                for i in self.view.lbx_jobs.curselection():
                    self.view.lbx_jobs.select_clear(i)
                self.view.lbl_explain["text"] = ''

        # カウントダウン時に実行する処理
        logger.debug(f"カウントダウン開始 {count}")
        self.view.update_count(count)   # 画面表示を更新
        self.beep(count)                # 最後の3秒で音を鳴らす

    def abort_cd(self, event=None):
        """
        カウントダウンの中断
        """
        try:
            self.view.after_cancel(self.after_id)   # afterをキャンセル
            self.que.clear()                        # キューをクリア
        except (NameError, AttributeError):
            pass

    def beep(self, count:int):
        """
        残り3秒になったら音を鳴らす
        Args:
            int:    残り時間
        """
        if count > 3: return
        f_d = {False:(440, 500), True:(880, 1000)}  # 時報のような音(ラ、ラ、高いラ)
        ws.Beep(f_d[count == 0][0], f_d[count == 0][1])

class App(tk.Tk):
    """
    アプリケーションクラス
    """
    def __init__(self) -> None:
        """
        コンストラクタ：操作画面クラスと制御クラスを作成し関連付ける
        """
        super().__init__()

        self.title("カウントダウンタイマー")      # タイトル

        my_model = MyModel()

        my_frame = MyFrame(self)                # MyFrameクラス(V)のインスタンス作成
        my_frame.pack()

        my_ctr = MyControl(my_model, my_frame)  # 制御クラス(C)のインスタンス作成
        my_frame.set_my_ctr(my_ctr)             # ビューにMyControlクラスを設定

if __name__ == '__main__':
    # logger setting
    LOGLEVEL = "INFO"   # ログレベル('CRITICAL','FATAL','ERROR','WARN','WARNING','INFO','DEBUG','NOTSET')
    logger = getLogger()
    handler = StreamHandler()	# このハンドラーを使うとsys.stderrにログ出力
    handler.setLevel(LOGLEVEL)
    # ログ出形式を定義 時:分:秒.ミリ秒 L:行 M:メソッド名 T:スレッド名 コメント
    handler.setFormatter(Formatter("{asctime}.{msecs:.0f} {name} L:{lineno:0=3} T:{threadName} M:{funcName} : {message}", "%H:%M:%S", "{"))
    logger.setLevel(LOGLEVEL)
    logger.addHandler(handler)
    logger.propagate = False
    logger.debug("start log")

    app = App()
    app.mainloop()
