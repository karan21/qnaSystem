# -*- coding: utf-8 -*-
# try something like
POSTS_PER_PAGE=10

def index():
    page=request.args(0,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    if(len(request.args) == 2):
        category = getcategory(request.args(1))
        questions=db(db.question.category_id==category.id).select(orderby=~db.question.created_on,limitby=(start,stop))
    else:
        questions=db(db.question).select(orderby=~db.question.created_on,limitby=(start,stop))
    list=[]
    for question in questions:
        answers=db(db.answer.question_id==question.id).select()
        print question.id
        print len(answers)
        list.append(len(answers))
    return locals()

def getcategory(category_nm):
    #category_nm=request.args(1)
    category=db.category(category_name=category_nm)
    if not category:
        session.flash='requested page not found'
        redirect(URL('index'))
    return category

# @auth.requires_login()
# def add_comm():
#     answer_id=request.args(0,cast=int)
#     db.comm.answer_id.default=answer_id
#     form=SQLFORM(db.comm).process(next='view_question/[id]')
#     return locals()

@auth.requires_login()
def add_answer():
    q_id=request.vars.question_id
    ans_body = request.vars.answer
    db.answer.insert(question_id=q_id,answer_body=ans_body)
    print "add answer here"
    redirect(URL('view_question',args=q_id))

@auth.requires_login()
def add_comment():
    a_id=request.vars.answer_id
    q_id=request.vars.ques_id
    comment_body = request.vars.comment
    db.comm.insert(answer_id=a_id,comm_body=comment_body)
    print "comment added"
    comments = db(db.comm.answer_id==a_id).select(orderby=~db.comm.created_on)
    str_div = ""
#     for comment in comments:
#         str_div = str_div + "<div class = \"row well-sm\"> <div class=\"col-sm-2\"> </div> <div class=\"col-sm-8\">"+comment.comm_body+"<hr/></div</div>"
    #return DIV(str_div)
    redirect(URL('view_question',args=q_id))

@auth.requires_login()
def add_question():
    category=getcategory(request.args(0))
    db.question.category_id.default=category.id
    form=SQLFORM(db.question).process(next='view_question/[id]')
    return locals()

@auth.requires_login()
def edit_question():
    question_id=request.args(0,cast=int)
    form=SQLFORM(db.question,question_id).process(next='view_question/[id]')
    return locals()

def list_questions_by_datetime():
    category=getcategory()
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.question.category_id==category.id).select(orderby=~db.question.created_on,limitby=(start,stop))
    return locals()

def list_questions_by_vote():
    category=getcategory()
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.question.category_id==category.id).select(orderby=~db.question.question_vote,limitby=(start,stop))
    return locals()

def list_questions_by_author():
    user_id=request.args(0,cast=int)
    quora=request.args(1,cast=int,default=0)
#     (T('Politics'),False,URL('sof_controller','index',args=["0","politics"])),
    # page=request.args(1,cast=int,default=0)
    if (quora==0):
        rows=db(db.question.created_by==user_id).select(orderby=~db.question.created_on)
    else:
        rows=db(db.answer.created_by==user_id).select(orderby=~db.question.created_on)
    return locals()

@auth.requires_login()
def view_question():
    print "in view question", request.args
    id=request.args(0,cast=int)
    post=db.question(id) or redirect(URL('index'))
    answers=db(db.answer.question_id==post.id).select(orderby=~db.answer.created_on)
    post.update_record(question_click_count=post.question_click_count+1)
    comments = []
    for answer in answers:
        comm = db(db.comm.answer_id==answer.id).select(orderby=~db.comm.created_on)
        comments.append(comm)
    following = db.bookmark(question_id=id,created_by=auth.user.id)
    if not following:
        isFollowing  = 0
    else:
        isFollowing  = 1
    return locals()

@auth.requires_login()
def vote_question():
    vars=request.args
    if len(vars)>0 and auth.user:
        id=vars[0]
        print "id:"
        print id
        direction=+1 if vars[1]=='up' else -1
        post2=db.answer(id)
#         print "direction"
#         print direction
#         print "user"
#         print auth.user.first_name
#         print "post"
#         print post
        if post2:
#             print "hello"
            vote=db.answer_vote(answer_id=id,created_by=auth.user.id)
#             print "vote"
#             print vote
#             print "empty"
            if not vote:
                post2.update_record(answer_vote=post2.answer_vote+direction)
                db.answer_vote.insert(answer_id=id,answer_score=direction)
            else:
                if vote.answer_score!=direction:
                    post2.update_record(answer_vote=post2.answer_vote+direction*2)
                    vote.update_record(answer_score=direction)
                else:
                    print "found"
    print "voted:"
    print post2.answer_vote
    return DIV(post2.answer_vote)


@auth.requires_login()
def vote_answer():
    vars=request.args
    if len(vars)>0 and auth.user:
        id=vars[0]
        print "id:"
        print id
        direction=+1 if vars[1]=='up' else -1
        post=db.question(id)
        print "direction"
        print direction
        print "user"
        print auth.user.first_name
        print "post"
        print post
        if post:
            print "hello"
            vote=db.question_vote(question_id=id,created_by=auth.user.id)
            print "vote"
            print vote
            print "empty"
            if not vote:
                print "not found"
                post.update_record(question_vote=post.question_vote+direction)
                db.question_vote.insert(question_id=id,question_score=direction)
            else:
                if vote.question_score!=direction:
                    post.update_record(question_vote=post.question_vote+direction*2)
                    vote.update_record(question_score=direction)
                else:
                    print "found"
    return DIV(post.question_vote)


@auth.requires_login()
def vote_comm():
    comm_id=request.args(0,cast=int)
    direction=request.args(1)
    return locals()
@auth.requires_login()
def bookmark():
    question_id = request.args(0,cast=int)
    print "request received"
    if request.args[1] == "follow":
        db.bookmark.insert(question_id=question_id)
        return "<button type=\"button\" class=\"btn btn-default btn-sm\" onclick=\"ajax('/sf/sof_controller/bookmark/"+request.args[0]+"/unfollow',[],'bookmark')\"><span class=\"glyphicon glyphicon-star\"></span>Remove Bookmark</button>"
#         return DIV(<button type="button" class="btn btn-default btn-sm" onclick="ajax('{{=URL('bookmark',args=(post.id,'unfollow'))}}',[],'bookmark')">Unfollow</button>)
    else:
        db(db.bookmark.question_id == question_id and db.bookmark.created_by == auth.user ).delete()
        return "<button type=\"button\" class=\"btn btn-default btn-sm\" onclick=\"ajax('/sf/sof_controller/bookmark/"+request.args[0]+"/follow',[],'bookmark')\"><span class=\"glyphicon glyphicon-star-empty\"></span>Bookmark</button>"
#         return DIV('<button type="button" class="btn btn-default btn-sm" onclick="ajax(\'{{=URL(\'bookmark\',args=(post.id,\'follow\'))}}\',[],\'bookmark\')">Follow</button>')

@auth.requires_login()
def view_user():
    user_id=request.args(0,cast=int)
    questions = db(db.question.created_by==user_id).select(orderby=~db.question.created_on)
    answers  =  db(db.answer.created_by==user_id)._select(db.answer.question_id)
    answered_questions = db(db.question.id.belongs(answers)).select()
    following = db(db.bookmark.created_by==user_id)._select(db.bookmark.question_id)
    following_questions = db(db.question.id.belongs(following)).select()
    return locals()

@auth.requires_login()
def edit_question():
    print "ed ques"
    question_id=request.vars.hid_id
    print question_id
    print "ab"
    post=db.question(question_id) or redirect(URL('index'))
    post.update_record(question_title=request.vars.title)
    post.update_record(question_body=request.vars.body)
    redirect(URL('view_question',args=question_id))

@auth.requires_login()
def edit_answer():
    qu_id=request.vars.q_id
    answer_id=request.vars.ans_id
    post=db.answer(answer_id) or redirect(URL('index'))
    post.update_record(answer_body=request.vars.up_ans)
    redirect(URL('view_question',args=qu_id))

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login()
def insert_category():
    rows=db(db.category.category_name==request.vars.hiu_id).select()
    if not rows:
        db.category.insert(category_name=request.vars.hiu_id)
        redirect(URL('add_question',args=request.vars.hiu_id))
    else:
        redirect(URL('add_question',args=request.vars.hiu_id))

@auth.requires_login()
def dele_question():
    post_id=request.args(0,cast=int)
    db(db.question.id==post_id).delete()
    redirect(URL('index/0'))
@auth.requires_login()
def dele_answer():
    post_id=request.args(0,cast=int)
    db(db.answer.id==post_id).delete()
    redirect(URL('index/0'))

@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.question,linked_tables=['answer','comm'])
    return dict(grid=grid)
