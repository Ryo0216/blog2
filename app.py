from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# データベースの初期化
def init_db():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES posts(id))''')
    conn.commit()
    conn.close()

# インデックスページ（投稿の一覧）
@app.route('/')
def index():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts')
    posts = c.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# 投稿の詳細ページとコメント機能
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post_detail(id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # 投稿情報を取得
    c.execute('SELECT * FROM posts WHERE id = ?', (id,))
    post = c.fetchone()

    # コメント情報を取得
    c.execute('SELECT * FROM comments WHERE post_id = ?', (id,))
    comments = c.fetchall()

    if request.method == 'POST':
        comment_content = request.form['comment']
        if comment_content.strip():  # 空白のコメントを防ぐ
            c.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (id, comment_content))
            conn.commit()

    conn.close()
    return render_template('post.html', post=post, comments=comments)

# 投稿の作成ページ
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # コメントを削除
    c.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()

    # 元の投稿ページにリダイレクト
    post_id = request.form['post_id']
    return redirect(url_for('post_detail', id=post_id))

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # 関連するコメントを削除
    c.execute('DELETE FROM comments WHERE post_id = ?', (post_id,))
    
    # 投稿を削除
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# アプリケーションの起動
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
