from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, logout_user, login_user, current_user
from datetime import date,datetime

app= Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'Influencersync'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

#Models Database
class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(20), nullable = False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), default='active', nullable=False)
    def get_id(self):
        return self.user_id

class SponsorInformation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True,)
    email = db.Column(db.String(50), unique = True, nullable = False)
    industry = db.Column(db.String(50),nullable=False)
    brand = db.Column(db.String(50), nullable=False)

class InfluencerInformation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True,)
    email = db.Column(db.String(50), unique = True, nullable = False)
    category = db.Column(db.String(50),nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    reach = db.Column(db.String(50), nullable=False)

class Campaign(db.Model):
    campain_id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),nullable=False)
    name = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    sdate = db.Column(db.Date, nullable=False)
    edate = db.Column(db.Date, nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(500), nullable=False)

class Request(db.Model):
    influencer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campain_id'), primary_key=True)
    status = db.Column(db.String(10), default='inactive', nullable=False)
    requestor = db.Column(db.String(15), nullable=False)

app.app_context().push()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

@app.route('/home')
@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = Users.query.filter_by(username=username).first()

        if not user:
            if role == 'influencer':
                return redirect(url_for('influencer_registration'))
            elif role == 'sponsor':
                return redirect(url_for('sponsor_registration'))
            else:
                flash('Invalid role')
                return render_template('login.html')

        if user.password == password and user.username == username and user.role == role:
            if user.status != 'flagged':
                login_user(user)
                if role == 'influencer':
                    return redirect(url_for('influencer_dashboard'))
                elif role == 'sponsor':
                    return redirect(url_for('sponsor_dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                flash('Access Denied')
                return render_template('login.html')
        else:
            flash('Invalid Credentials')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/influencer_dashboard')
def influencer_dashboard():
    if current_user.role == 'influencer':
        detail = InfluencerInformation.query.filter_by(user_id = current_user.user_id).first()
        new = Request.query.filter_by(influencer_id = current_user.user_id,requestor='sponsor').all()

        req_list = []
        for request in new:
            if request.status == 'inactive':
                camp = Campaign.query.filter_by(campain_id = request.campaign_id).first()
                spon = SponsorInformation.query.filter_by(user_id = request.sponsor_id).first()
                req_list.append((camp,spon))

        active = Request.query.filter_by(influencer_id = current_user.user_id, status = 'active').all()

        acc_list = []
        for request in active:
            camp = Campaign.query.filter_by(campain_id = request.campaign_id).first()
            acc_list.append(camp)

        requested = Request.query.filter_by(influencer_id = current_user.user_id, status = 'inactive', requestor = 'influencer').all()

        requested_list = []
        for request in requested:
            camp = Campaign.query.filter_by(campain_id = request.campaign_id).first()
            requested_list.append(camp)

        return render_template('influencer_dashboard.html',info_detail=detail, new_request = req_list, your_camp=acc_list, request_list=requested_list)

@app.route('/ad_request')
def ad_request():
    
    return render_template('adrequest.html')
    

@app.route('/search_campaign',methods=['Get','POST'])
def search_campaign():
    spon_camp = []
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        
        all_camp = Campaign.query.all()

        req_list = []

        if name != '':
            for camp in all_camp:
                if name in camp.name or name == camp.name:
                    req_list.append(camp)

        elif category != '':
            for camp in all_camp:
                if category in camp.name or category == camp.category:
                    req_list.append(camp)
        else:
            flash('Please Enter input')
            return render_template('searchcampaign.html',msg='')

        if req_list != []:
            for camp in req_list:
                spon = SponsorInformation.query.filter_by(user_id = camp.sponsor_id).first()
                spon_camp.append((camp,spon))
        else:
            flash('Result not found')
            return render_template('searchcampaign.html',msg='')

        return render_template('searchcampaign.html', all_camps = spon_camp ,msg='search')

    return render_template('searchcampaign.html', all_camps = spon_camp ,msg='')

@app.route('/influencer_dashboard/update_profile',methods=['GET','POST'])
def update_profile():
    detail = InfluencerInformation.query.filter_by(user_id = current_user.user_id).first()
    if request.method == 'POST':
        email = request.form.get('email')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        category = request.form.get('category')

        detail.email = email
        detail.niche = niche
        detail.reach = reach
        detail.category = category

        db.session.add(detail)
        db.session.commit()

        detail = InfluencerInformation.query.filter_by(user_id = current_user.user_id).first()
        
        flash('Updated Successfully')
        return render_template('update profile.html', user=detail)
    
    return render_template('update profile.html', user=detail)

@app.route('/search_campaign_all')
def search_campaign_all():
    all_camp = Campaign.query.all()

    spon_camp = []

    for camp in all_camp:
        user = Users.query.filter_by(user_id = camp.sponsor_id).first()
        spon_camp.append((camp, user))

    return render_template('searchcampaign.html', all_camps = spon_camp, msg='all')

#------------------------------Influencer's Requests------------------#
@app.route('/send_request/<int:camp_id>/<int:spon_id>')
def send_request(camp_id, spon_id):
    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = current_user.user_id).first()

    if exist:
        camp = Campaign.query.filter_by(campain_id = camp_id).first()
        name = camp.name
        msg = f'Already requested to campaign: {name}'
        flash(msg)
        return redirect(url_for('search_campaign'))
    else:
        request = Request(
            campaign_id = camp_id,
            sponsor_id = spon_id,
            influencer_id = current_user.user_id,
            requestor = 'influencer'
        )
        db.session.add(request)
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))

#----------------------------Sponsor Dashboard------------------------#

@app.route('/sponsor_dashboard')
def sponsor_dashboard():
    camp = Campaign.query.filter_by(sponsor_id = current_user.user_id).all()

    spend=0
    for val in camp:
        spend+=val.budget

    all_requested = Request.query.filter_by(sponsor_id = current_user.user_id, requestor = 'sponsor').all()

    requested_camp = []

    for request in all_requested:
        if request.status=='inactive':
            inf = Users.query.filter_by(user_id = request.influencer_id).first()
            camp1 = Campaign.query.filter_by(campain_id = request.campaign_id).first()
            requested_camp.append((inf,camp1))

    exist = Request.query.filter_by(sponsor_id = current_user.user_id, requestor='influencer',status='inactive').all()

    new = []
    for request in exist:
        inf = Users.query.filter_by(user_id = request.influencer_id).first()
        camp1 = Campaign.query.filter_by(campain_id = request.campaign_id).first()
        new.append((camp1,inf))
    
    active = Request.query.filter_by(sponsor_id = current_user.user_id,status='active').all()

    ongoing=[]
    for data in active:
        user = Users.query.filter_by(user_id = data.influencer_id).first()
        camp2 = Campaign.query.filter_by(campain_id = data.campaign_id).first()
        ongoing.append((camp2,user))

    return render_template('sponsor_dashboard.html',requested_list=requested_camp,request_list=new,accept_list = ongoing, spends=spend, total = len(camp))


#---------------------------------------Search Influencer--------------------------#
@app.route('/search_influencer/<int:camp_id>',methods=['Get','POST'])
def search_influencer(camp_id):
    influ_list = []
    camp = Campaign.query.filter_by(campain_id = camp_id).first()
    if request.method == 'POST':
        niche = request.form.get('niche')
        category = request.form.get('category')

        if niche != '':
            influ = InfluencerInformation.query.filter_by(niche = niche).all()
            if influ == []:
                flash('Result not found')
                return render_template('searchinf.html',msg='',campain = camp)
            else:
                for inf in influ:
                    user = Users.query.filter_by(user_id = inf.user_id).first()
                    influ_list.append((inf,user))

        elif category != '':
            influ = InfluencerInformation.query.filter_by(category = category).all()
            print(influ)
            if influ == []:
                flash('Result not found')
                return render_template('searchinf.html',msg='',campain = camp)
            else:
                for inf in influ:
                    user = Users.query.filter_by(user_id = inf.user_id).first()
                    influ_list.append((inf,user))
        else:
            flash('Please Enter input')
            return render_template('searchinf.html',msg='',campain = camp)

        return render_template('searchinf.html',  influ_lists = influ_list,msg='search',campain = camp)
    
    return render_template('searchinf.html',campain = camp,  influ_lists = influ_list,msg='')

@app.route('/search_influencer_all/<int:camp_id>')
def search_influencer_all(camp_id):
    
    all_user = Users.query.all()
    
    all_influ = [user for user in all_user if user.role == 'influencer']

    detail_list = []

    for influencer in all_influ:
        detail = InfluencerInformation.query.filter_by(user_id = influencer.user_id).first()
        detail_list.append((influencer,detail))
    camp = Campaign.query.filter_by(campain_id = camp_id).first()
    return render_template('searchinf.html', campain = camp, details_list = detail_list, msg='all')

#=======================================Ad Management===================================#
#=======================================================================================#

#====================================Sponsor' Request=============================#
@app.route('/sponsor_request/<int:camp_id>/<int:user_id>')
def sponsor_request(camp_id, user_id):

    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = user_id).first()

    if exist:
        user = Users.query.filter_by(user_id=user_id).first()
        name = user.username
        msg = f'Already request sended to {name}'
        flash(msg)
        return redirect(url_for('search_influencer',camp_id = camp_id))

    else:
        request = Request(
            campaign_id = camp_id,
            sponsor_id = current_user.user_id,
            influencer_id = user_id,
            requestor = 'sponsor'
        )
        db.session.add(request)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))
    
@app.route('/sponsor_accept_request/<int:camp_id>/<int:influ_id>')
def sponsor_accept(camp_id, influ_id):
    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = influ_id, requestor='influencer').first()
    exist.status = 'active'
    db.session.add(exist)
    db.session.commit()
    return redirect(url_for("sponsor_dashboard"))

@app.route('/delete_requested/<int:inf_id>/<int:camp_id>') #Sponsor Delete Request#
def delete_requested(inf_id,camp_id):
    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = inf_id, requestor= 'sponsor').first()
    db.session.delete(exist)
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/influencer_accept_request/<int:camp_id>')
def influencer_accept(camp_id):
    exist = Request.query.filter_by(influencer_id = current_user.user_id, campaign_id = camp_id, requestor = 'sponsor').first()
    exist.status = 'active'
    db.session.add(exist)
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

@app.route('/influencer_cancel_request/<int:camp_id>')
def influencer_cancel_request(camp_id):
    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = current_user.user_id, requestor= 'influencer').first()
    db.session.delete(exist)
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

@app.route('/sponsor_reject/<int:camp_id>/<int:influ_id>')
def sponsor_reject(camp_id,influ_id):
    exist = Request.query.filter_by(campaign_id=camp_id, influencer_id = influ_id).first()
    db.session.delete(exist)
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/influencer_reject/<int:camp_id>')
def influencer_reject(camp_id):
    exist = Request.query.filter_by(campaign_id=camp_id, influencer_id = current_user.user_id).first()
    db.session.delete(exist)
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))



#======================================================End Ad Management============================#
#===================================================================================================#

@app.route('/campaign')
def campaign():
    all_camp1 = Campaign.query.filter_by(sponsor_id = current_user.user_id).all()
    
    return render_template('campaigns.html' , all_camp=all_camp1)

@app.route('/delete/campaign/<int:camp_id>')
def delete_campaign(camp_id):
    camp = Campaign.query.filter_by(campain_id = camp_id).first()
    db.session.delete(camp)
    db.session.commit()

    all_camp1 = Campaign.query.filter_by(sponsor_id = current_user.user_id).all()

    return render_template('campaigns.html' , all_camp=all_camp1)

@app.route('/update/campaign/<int:camp_id>', methods=['GET' , 'POST'])
def update_campaign(camp_id):
    camp = Campaign.query.filter_by(campain_id = camp_id).first()
    if request.method == 'POST':
        camp.name = request.form.get('name')
        camp.budget = request.form.get('budget')
        camp.goal = request.form.get('goal')
        camp.category = request.form.get('category')
        camp.bio = request.form.get('bio')
        camp.sdate = datetime.strptime(request.form['start-date'], '%Y-%m-%d').date()
        camp.edate = datetime.strptime(request.form['end-date'], '%Y-%m-%d').date()

        db.session.add(camp)
        db.session.commit()

        all_camp1 = Campaign.query.filter_by(sponsor_id = current_user.user_id).all()
        return render_template('campaigns.html' , all_camp=all_camp1)

    return render_template('crtcamp.html', msg="update" , campaign=camp)

@app.route('/create_campaign', methods=['GET','POST'])
def create_campaign():
    if request.method == 'POST':
        name = request.form.get('name')
        budget = request.form.get('budget')
        goal = request.form.get('goal')
        category = request.form.get('category')
        bio = request.form.get('bio')

        sdate = datetime.strptime(request.form['start-date'], '%Y-%m-%d').date()
        edate = datetime.strptime(request.form['end-date'], '%Y-%m-%d').date()

        camp = Campaign(
            name=name, budget = budget, goal = goal, category=category, bio=bio,
            edate=edate, sdate=sdate, sponsor_id = current_user.user_id
        )

        db.session.add(camp)
        db.session.commit()

        return redirect(url_for('campaign'))

    return render_template('crtcamp.html', msg="create")
#===============================================================Admin Dashboard===========================#
@app.route('/admin_dashboard')
def admin_dashboard():
    cinflu = 0
    cspon = 0
    auser = 0
    fuser=0
    all_user = Users.query.all()
    for user in all_user:
        if user.status=='active':
            auser+=1
        elif user.status=='flagged':
            fuser+=1
        if user.role !='admin':
            if user.role=='influencer':
                cinflu+=1
            else:
                cspon+=1
    camp = Campaign.query.all()
    active_camp = Request.query.filter_by(status='active').all()
    return render_template('admin_dashboard.html',countinflu=cinflu, countspon=cspon,flag=fuser, active=auser, total_user=len(all_user),
                            total_camp = len(camp), campaign=len(active_camp))

@app.route('/admin_dashboard/manage_user')
def admin_manage():
    all_user = Users.query.all()
    total=0
    user_list=[]
    for user in all_user:
        if user.role!='admin':
            total+=1
            if user.role=='sponsor':
                spon = SponsorInformation.query.filter_by(user_id=user.user_id).first()
                email = spon.email
                user_list.append((user,email))
            elif user.role=='influencer':
                influ = InfluencerInformation.query.filter_by(user_id=user.user_id).first()
                email = influ.email
                user_list.append((user,email))
    return render_template('manage_users.html',users_list=user_list,users=total)

@app.route('/admin_dashboard/user_details/<int:id>')
def user_detail(id):
    user1 = Users.query.filter_by(user_id = id).first()
    spon = SponsorInformation.query.filter_by(user_id = id).first()
    influ = InfluencerInformation.query.filter_by(user_id = id).first()

    if spon:
        camp = Campaign.query.filter_by(sponsor_id = id).all()
        return render_template('admin_user_view.html', user = [(spon,user1)], campaign = camp)
    elif influ:
        req = Request.query.filter_by(influencer_id = id, status='active').all()
        camp=[]
        for temp in req:
            camp.append(Campaign.query.filter_by(campain_id = temp.campaign_id).first())
        
        return render_template('admin_user_view.html',user=[(influ,user1)], campaign = camp )

    return render_template('admin_user_view.html')


@app.route('/admin/user/flag/<int:id>')
def flag(id):
    user = Users.query.filter_by(user_id=id).first()
    user.status='flagged'
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin_manage'))

@app.route('/admin/user/unflag/<int:id>')
def unflag(id):
    user = Users.query.filter_by(user_id=id).first()
    user.status='active'
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin_manage'))

@app.route('/admin/user/flag_delete/<int:id>')
def flag_delete(id):
    user = Users.query.filter_by(user_id=id).first()

    if user.role=='sponsor':
        request = Request.query.filter_by(sponsor_id=user.user_id).all()
        for spon in request:
            db.session.delete(spon)
            db.session.commit()
        campaign = Campaign.query.filter_by(sponsor_id = user.user_id).all()
        for camp in campaign:
            db.session.delete(camp)
            db.session.commit()
        infor = SponsorInformation.query.filter_by(user_id = user.user_id).first()
        db.session.delete(infor)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_manage'))
    
    elif user.role == 'influencer':
        request = Request.query.filter_by(influencer_id=user.user_id).all()
        for spon in request:
            db.session.delete(spon)
            db.session.commit()
        infor = InfluencerInformation.query.filter_by(user_id = user.user_id).first()
        db.session.delete(infor)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_manage'))


@app.route('/admin_dashboard/all_campaign')
def admin_campaign():

    all_camp = Request.query.filter_by(status='active').all()

    detail_of_campaign =[]
    for camp in all_camp:
        inf = Users.query.filter_by(user_id = camp.influencer_id).first()
        spon = Users.query.filter_by(user_id = camp.sponsor_id).first()
        camp1 = Campaign.query.filter_by(campain_id = camp.campaign_id).first()
        detail_of_campaign.append((inf,spon,camp1))
    return render_template('admin camp.html',detail=detail_of_campaign)

@app.route('/admin/delete/campaign/<int:camp_id>/<int:inf_id>')
def admin_delete_campaign(camp_id, inf_id):
    exist = Request.query.filter_by(campaign_id = camp_id, influencer_id = inf_id).first()
    db.session.delete(exist)
    db.session.commit()
    return redirect(url_for('admin_campaign'))



#==========================================================================================================#

@app.route('/sponsor_registration', methods=['GET','POST'])
def sponsor_registration():
    if request.method == 'POST':
        #data save in databse
        username = request.form.get('username')
        email = request.form.get('email')
        brand_name = request.form.get('brand-name')
        industry = request.form.get('industry')
        password = request.form.get('password')
        role = request.form.get('role')

        if Users.query.filter_by(username=username).first():
            return render_template('sp reg.html',msg='Username Not Available')

        else:
            user = Users(username=username, password=password,
                        role=role)
            db.session.add(user)
            db.session.commit()

            user = Users.query.filter_by(username=username).first()

            detail = SponsorInformation(user_id = user.user_id,
                                        email=email, brand=brand_name,
                                        industry=industry)
            
            db.session.add(detail)
            db.session.commit()

            flash('Successfully Registered')
            return redirect(url_for('login')) 

        #sponsor = SponsorInformation()
    return render_template('sp reg.html')

@app.route('/influencer_registration', methods=['GET','POST'])
def influencer_registration():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        category = request.form.get('category')

        if Users.query.filter_by(username=username).first():
            return render_template('inf reg.html',msg='Username Not Available')
        else:
            user = Users(username=username, password=password,
                        role=role)
            db.session.add(user)
            db.session.commit()

            user = Users.query.filter_by(username=username).first()

            inf = InfluencerInformation(
                user_id = user.user_id,
                email = email,
                niche = niche,
                reach = reach,
                category = category
            )

            db.session.add(inf)
            db.session.commit()

            flash('Successfully Registered')
            return redirect(url_for('login')) 

    return render_template('inf reg.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)