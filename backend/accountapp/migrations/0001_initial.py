# Generated by Django 4.2.9 on 2024-02-19 18:19

import accountapp.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('username', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z_]{5,20}$', '5-20글자 사이의 숫자,영문,언더바만 가능합니다!')])),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('school', models.CharField(choices=[('0', 'GIST (광주과학기술원)'), ('1', 'KAIST (한국과학기술원)'), ('2', 'KENTECH (한국에너지공과대학교)'), ('3', 'UNIST (울산과학기술원)'), ('4', 'DGIST (대구경북과학기술원)'), ('5', '가천대학교'), ('6', '가톨릭관동대학교'), ('7', '가톨릭꽃동네대학교'), ('8', '가톨릭대학교'), ('9', '가톨릭상지대학교'), ('10', '감리교신학대학교'), ('11', '강남대학교'), ('12', '강동대학교'), ('13', '강릉영동대학교'), ('14', '강서대학교 (KC대학교)'), ('15', '강원관광대학교'), ('16', '강원대학교 춘천캠퍼스'), ('17', '강원대학교 삼척도계캠퍼스'), ('18', '강원도립대학교'), ('19', '거제대학교'), ('20', '건국대학교 서울캠퍼스'), ('21', '건국대학교 GLOCAL캠퍼스'), ('22', '건양대학교'), ('23', '건양사이버대학교'), ('24', '겐트대학교'), ('25', '경기과학기술대학교'), ('26', '경기대학교 수원캠퍼스'), ('27', '경기대학교 서울캠퍼스'), ('28', '경남대학교'), ('29', '경남도립거창대학'), ('30', '경남도립남해대학'), ('31', '경남정보대학교 (KIT)'), ('32', '경동대학교 양주캠퍼스'), ('33', '경동대학교 고성캠퍼스'), ('34', '경동대학교 원주캠퍼스'), ('35', '경민대학교'), ('36', '경복대학교'), ('37', '경북과학대학교'), ('38', '경북대학교 대구캠퍼스'), ('39', '경북대학교 상주캠퍼스'), ('40', '경북도립대학교'), ('41', '경북보건대학교'), ('42', '경북전문대학교'), ('43', '경상국립대학교 (경상대)'), ('44', '경상국립대학교 칠암캠퍼스(경남과기대)'), ('45', '경성대학교'), ('46', '경운대학교'), ('47', '경인교육대학교'), ('48', '경인여자대학교'), ('49', '경일대학교'), ('50', '경주대학교'), ('51', '경찰대학'), ('52', '경희대학교 국제캠퍼스'), ('53', '경희대학교 서울캠퍼스'), ('54', '경희사이버대학교'), ('55', '계명대학교'), ('56', '계명문화대학교'), ('57', '계원예술대학교'), ('58', '고구려대학교'), ('59', '고려대학교 서울캠퍼스'), ('60', '고려대학교 세종캠퍼스'), ('61', '고려사이버대학교'), ('62', '고신대학교'), ('63', '공주교육대학교'), ('64', '광신대학교'), ('65', '광양보건대학교'), ('66', '광운대학교'), ('67', '광주가톨릭대학교'), ('68', 'ICT폴리텍대학'), ('69', '광주교육대학교'), ('70', '광주대학교'), ('71', '광주보건대학교'), ('72', '광주여자대학교'), ('73', '구미대학교'), ('74', '국립강릉원주대학교 강릉캠퍼스'), ('75', '국립강릉원주대학교 원주캠퍼스'), ('76', '국립공주대학교'), ('77', '국립군산대학교'), ('78', '국립금오공과대학교'), ('79', '국립목포대학교'), ('80', '국립부경대학교'), ('81', '국립순천대학교'), ('82', '국립안동대학교'), ('83', '국립창원대학교'), ('84', '국립한국교통대학교'), ('85', '국립한국해양대학교'), ('86', '국립한밭대학교'), ('87', '국민대학교'), ('88', '국제대학교'), ('89', '국제사이버대학교'), ('90', '국제예술대학교'), ('91', '군산간호대학교'), ('92', '군장대학교'), ('93', '극동대학교'), ('94', '글로벌사이버대학교'), ('95', '금강대학교'), ('96', '기독간호대학교'), ('97', '김천대학교'), ('98', '김포대학교'), ('99', '김해대학교'), ('100', '나사렛대학교'), ('101', '남부대학교'), ('102', '남서울대학교'), ('103', '농협대학교'), ('104', '단국대학교 죽전캠퍼스'), ('105', '단국대학교 천안캠퍼스'), ('106', '대경대학교'), ('107', '대구가톨릭대학교'), ('108', '가야대학교'), ('109', '대구공업대학교'), ('110', '대구과학대학교'), ('111', '대구교육대학교'), ('112', '대구대학교'), ('113', '대구보건대학교'), ('114', '대구사이버대학교'), ('115', '대구예술대학교'), ('116', '대구한의대학교'), ('117', '대덕대학교'), ('118', '대동대학교'), ('119', '대림대학교'), ('120', '대신대학교'), ('121', '대원대학교'), ('122', '대전가톨릭대학교'), ('123', '대전과학기술대학교 (DST)'), ('124', '대전대학교'), ('125', '대전보건대학교 (HIT)'), ('126', '대전신학대학교'), ('127', '대진대학교'), ('128', '덕성여자대학교'), ('129', '동강대학교'), ('130', '동국대학교 서울캠퍼스'), ('131', '동국대학교 WISE캠퍼스'), ('132', '동남보건대학교'), ('133', '동덕여자대학교'), ('134', '동명대학교'), ('135', '동서대학교'), ('136', '동서울대학교'), ('137', '동신대학교'), ('138', '동아대학교'), ('139', '동아방송예술대학교 (DIMA)'), ('140', '동아보건대학교'), ('141', '동양대학교'), ('142', '동양미래대학교'), ('143', '동원과학기술대학교'), ('144', '동원대학교'), ('145', '동의과학대학교 (DIT)'), ('146', '동의대학교'), ('147', '두원공과대학교'), ('148', '디지털서울문화예술대학교'), ('149', '라사라패션직업전문학교'), ('150', '루터대학교'), ('151', '마산대학교'), ('152', '명지대학교 인문캠퍼스'), ('153', '명지대학교 자연캠퍼스'), ('154', '명지전문대학'), ('155', '목원대학교'), ('156', '목포가톨릭대학교'), ('157', '목포과학대학교'), ('158', '목포해양대학교'), ('159', '문경대학교'), ('160', '배재대학교'), ('161', '배화여자대학교'), ('162', '백석대학교'), ('163', '백석문화대학교'), ('164', '백석예술대학교'), ('165', '백제예술대학교'), ('166', '부산가톨릭대학교'), ('167', '부산경상대학교'), ('168', '부산과학기술대학교'), ('169', '부산교육대학교'), ('170', '부산대학교'), ('171', '부산디지털대학교'), ('172', '부산보건대학교'), ('173', '부산여자대학교'), ('174', '부산예술대학교'), ('175', '부산외국어대학교'), ('176', '부산장신대학교'), ('177', '부천대학교'), ('178', '사이버한국외국어대학교'), ('179', '삼육대학교'), ('180', '삼육보건대학교'), ('181', '상명대학교 서울캠퍼스'), ('182', '상명대학교 천안캠퍼스'), ('183', '상지대학교'), ('184', '서강대학교'), ('185', '서경대학교'), ('186', '서라벌대학교'), ('187', '서영대학교 파주캠퍼스'), ('188', '서영대학교 광주캠퍼스'), ('189', '서울과학기술대학교'), ('190', '서울교육대학교'), ('191', '서울기독대학교'), ('192', '서울대학교'), ('193', '서울디지털대학교'), ('194', '서울사이버대학교'), ('195', '서울시립대학교'), ('196', '서울신학대학교'), ('197', '서울여자간호대학교'), ('198', '서울여자대학교'), ('199', '서울예술대학교'), ('200', '서울장신대학교'), ('201', '서울한영대학교'), ('202', '서울현대전문학교'), ('203', '서울호텔관광실용전문학교'), ('204', '서원대학교'), ('205', '서일대학교'), ('206', '서정대학교'), ('207', '서해대학교'), ('208', '선린대학교'), ('209', '선문대학교'), ('210', '성결대학교'), ('211', '성공회대학교'), ('212', '성균관대학교 인사캠퍼스'), ('213', '성균관대학교 자과캠퍼스'), ('214', '성신여자대학교'), ('215', '성운대학교'), ('216', '세경대학교'), ('217', '세명대학교'), ('218', '세종대학교'), ('219', '세종사이버대학교'), ('220', '세한대학교 당진캠퍼스'), ('221', '세한대학교 영암캠퍼스'), ('222', '송곡대학교'), ('223', '송원대학교'), ('224', '송호대학교'), ('225', '수성대학교'), ('226', '수원가톨릭대학교'), ('227', '수원과학대학교'), ('228', '수원대학교'), ('229', '수원여자대학교'), ('230', '숙명여자대학교'), ('231', '순복음총회신학교'), ('232', '순천제일대학교'), ('233', '순천향대학교'), ('234', '숭실대학교'), ('235', '숭실사이버대학교'), ('236', '숭의여자대학교'), ('237', '신구대학교'), ('238', '신라대학교'), ('239', '신성대학교'), ('240', '신안산대학교'), ('241', '신한대학교'), ('242', '아신대학교'), ('243', '아주대학교'), ('244', '아주자동차대학'), ('245', '안동과학대학교'), ('246', '안산대학교'), ('247', '안양대학교'), ('248', '여주대학교'), ('249', '연성대학교'), ('250', '연세대학교 신촌캠퍼스'), ('251', '연세대학교 미래캠퍼스'), ('252', '연암공과대학교'), ('253', '연암대학교'), ('254', '영남대학교'), ('255', '영남신학대학교'), ('256', '영남외국어대학'), ('257', '영남이공대학교'), ('258', '영산대학교 (와이즈유)'), ('259', '영산선학대학교'), ('260', '영진사이버대학교'), ('261', '영진전문대학교'), ('262', '예수대학교'), ('263', '예원예술대학교 양주캠퍼스'), ('264', '예원예술대학교 임실캠퍼스'), ('265', '오산대학교'), ('266', '용인대학교'), ('267', '용인예술과학대학교'), ('268', '우석대학교 진천캠퍼스'), ('269', '우석대학교 전주캠퍼스'), ('270', '우송대학교'), ('271', '우송정보대학'), ('272', '울산과학대학교'), ('273', '울산대학교'), ('274', '웅지세무대학교'), ('275', '원광대학교'), ('276', '원광디지털대학교'), ('277', '원광보건대학교'), ('278', '위덕대학교'), ('279', '유원대학교 (U1대학교)'), ('280', '유타대학교'), ('281', '유한대학교'), ('282', '을지대학교 성남캠퍼스'), ('283', '을지대학교 의정부/대전캠퍼스'), ('284', '이화여자대학교'), ('285', '인덕대학교'), ('286', '인제대학교'), ('287', '인천가톨릭대학교'), ('288', '인천대학교'), ('289', '인천재능대학교'), ('290', '인하공업전문대학교'), ('291', '인하대학교'), ('292', '장로회신학대학교'), ('293', '장안대학교'), ('294', '전남과학대학교'), ('295', '전남대학교 광주캠퍼스'), ('296', '전남대학교 여수캠퍼스'), ('297', '전남도립대학교'), ('298', '전북과학대학교'), ('299', '전북대학교'), ('300', '전주교육대학교'), ('301', '전주기전대학'), ('302', '전주대학교'), ('303', '전주비전대학교'), ('304', '정석대학'), ('305', '정화예술대학교'), ('306', '제주관광대학교'), ('307', '제주국제대학교'), ('308', '제주대학교'), ('309', '제주한라대학교'), ('310', '조선간호대학교'), ('311', '조선대학교'), ('312', '조선이공대학교'), ('313', '중부대학교 충청캠퍼스'), ('314', '중부대학교 고양캠퍼스'), ('315', '중앙대학교 서울캠퍼스'), ('316', '중앙대학교 다빈치캠퍼스'), ('317', '중앙승가대학교'), ('318', '중원대학교'), ('319', '진주교육대학교'), ('320', '진주보건대학교'), ('321', '차의과학대학교'), ('322', '창신대학교'), ('323', '창원문성대학교'), ('324', '청강문화산업대학교'), ('325', '청암대학교'), ('326', '청운대학교 인천캠퍼스'), ('327', '청운대학교 홍성캠퍼스'), ('328', '청주교육대학교'), ('329', '청주대학교'), ('330', '초당대학교'), ('331', '총신대학교'), ('332', '추계예술대학교'), ('333', '춘천교육대학교'), ('334', '춘해보건대학교'), ('335', '충남대학교'), ('336', '충남도립대학교'), ('337', '충북대학교'), ('338', '충북도립대학교'), ('339', '충북보건과학대학교'), ('340', '충청대학교'), ('341', '칼빈대학교'), ('342', '평택대학교'), ('343', '포항공과대학교 (POSTECH)'), ('344', '포항대학교'), ('345', '한경국립대학교 (한경대)'), ('346', '한경국립대학교 평택캠퍼스(한국복지대)'), ('347', '한국골프대학교'), ('348', '한국공학대학교 (한국산업기술대학교)'), ('349', '한국관광대학교'), ('350', '한국교원대학교'), ('351', '한국국제대학교 (IUK)'), ('352', '한국기술교육대학교'), ('353', '한국농수산대학'), ('354', '한국뉴욕주립대학교 (SUNY Korea)'), ('355', '한국방송통신대학교'), ('356', '한국복지사이버대학'), ('357', '한국성서대학교'), ('358', '한국승강기대학교'), ('359', '한국열린사이버대학교'), ('360', '한국영상대학교'), ('361', '한국예술종합학교'), ('362', '한국외국어대학교 서울캠퍼스'), ('363', '한국외국어대학교 글로벌캠퍼스'), ('364', '한국전통문화대학교'), ('365', '한국조지메이슨대학교'), ('366', '한국체육대학교'), ('367', '한국침례신학대학교'), ('368', '한국폴리텍대학교'), ('369', '한국항공대학교'), ('370', '한남대학교'), ('371', '한동대학교'), ('372', '한라대학교'), ('373', '한려대학교'), ('374', '한림대학교'), ('375', '한림성심대학교'), ('376', '한서대학교'), ('377', '한성대학교'), ('378', '한세대학교'), ('379', '한신대학교'), ('380', '한양대학교 서울캠퍼스'), ('381', '한양대학교 ERICA캠퍼스'), ('382', '한양사이버대학교'), ('383', '한양여자대학교'), ('384', '한영대학교'), ('385', '한일장신대학교'), ('386', '협성대학교'), ('387', '혜전대학교'), ('388', '호남대학교'), ('389', '호남신학대학교'), ('390', '호산대학교'), ('391', '호서대학교'), ('392', '호원대학교'), ('393', '홍익대학교 서울캠퍼스'), ('394', '홍익대학교 세종캠퍼스'), ('395', '화성의과학대학교 (신경대학교)'), ('396', '화신사이버대학교'), ('397', '신경주대학교')], max_length=20, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', accountapp.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, default='익명의 몽글', max_length=13)),
                ('profile_pic', models.ImageField(blank=True, default='default.png', null=True, upload_to='profile_pics/')),
                ('bio', models.TextField(blank=True, max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
