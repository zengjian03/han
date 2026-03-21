#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/11/21 18:34
# @file    : 爬虫模板.min.py
S='@page'
R='数据列表'
Q='type_name'
P='请求头'
D=';'
N='主页url'
M='jx'
L=print
K=Exception
C='vod_pic'
I='parse'
H='vod_remarks'
G='vod_id'
F='vod_name'
E='list'
B=''
import json,re,sys,requests as J
from pyquery import PyQuery as O
sys.path.append('..')
from base.spider import Spider as A
class Spider(A):
	def __init__(A):super().__init__();A.name=B;A.error_play_url='https://kjjsaas-sh.oss-cn-shanghai.aliyuncs.com/u/3401405881/20240818-936952-fc31b16575e80a7562cdb1f81a39c6b0.mp4'
	def getName(A):return A.name
	def init(A,extend='{}'):
		C=extend
		try:
			if C.startswith('http'):D=J.get(C);A.extend=D.json()
			else:A.extend=json.loads(C)
			A.name=A.extend.get('name',B)
		except K as E:L(E);A.extend={}
	def homeContent(A,filter):
		T='class';S={T:[],'filters':{},E:[],I:0,M:0};U=A.extend[N]
		def V(doc_html):
			B=A.extend['分类'].split(D);G=B[0];H=B[1];I=B[2];J=B[3]
			for E in doc_html(G).items():
				F=A.fun_css(E,H);C=A.fun_css(E,I);C=A.fun_re(C,J)
				if F in A.extend['分类过滤']:continue
				S[T].append({'type_id':C,Q:F})
		def W(doc_html):
			B='首页数据';K=A.extend[B][R]
			for I in doc_html(K).items():J=A.extend[B][G].split(D);L=A.extend[B][F];M=A.extend[B][C];N=A.extend[B][H];S[E].append({G:A.fun_re(A.fun_css(I,J[0]),J[1]),F:A.fun_css(I,L),C:A.fun_css(I,M),H:A.fun_css(I,N)})
		try:X=J.get(U,headers=A.extend[P]);B=O(X.text.encode());V(B);W(B)
		except K as Y:L(Y)
		return S
	def categoryContent(A,cid,page,filter,ext):
		Q={E:[],I:0,M:0};B=A.extend[N]+A.extend['分类url'].replace('@class',cid).replace(S,page)
		def T(doc_html):
			B='分类数据';K=A.extend[B][R]
			for I in doc_html(K).items():J=A.extend[B][G].split(D);L=A.extend[B][F];M=A.extend[B][C];N=A.extend[B][H];Q[E].append({G:A.fun_re(A.fun_css(I,J[0]),J[1]),F:A.fun_css(I,L),C:A.fun_css(I,M),H:A.fun_css(I,N)})
		try:U=J.get(B,headers=A.extend[P]);V=O(U.text.encode());T(V)
		except K as W:L(W)
		return Q
	def detailContent(A,did):
		b='$$$';a='vod_play_url';Z='vod_play_from';Y='vod_content';X='vod_director';W='vod_actor';V='vod_area';U='vod_year';C='详情数据';S={E:[],I:0,M:0};T=did[0];c=A.extend[N]+A.extend['详情url'].replace('@ids',T);D={Q:B,G:T,F:B,H:B,U:B,V:B,W:B,X:B,Y:B,Z:B,a:B}
		def d(doc_html):
			E=A.extend[C]['线路列表'];F=A.extend[C]['线路名字'];B=[]
			for G in doc_html(E).items():H=A.fun_css(G,F);B.append(H)
			D[Z]=b.join(B)
		def e(doc_html):
			H=A.extend[C]['播放列表'];I=A.extend[C]['选集列表'];J=A.extend[C]['选集名字'];K=A.extend[C]['选集地址'];E=[]
			for F in doc_html(H).items():
				G=[]
				for L in F(I).items():
					M=A.fun_css(L,J);B=A.fun_css(F,K)
					if not B.startswith(('http://','https://')):B=A.extend[N]+B
					G.append(f"{M}${B}")
				E.append('#'.join(G))
			D[a]=b.join(E)
		def f(doc_html):B=doc_html;E=A.extend[C]['标题'];G=A.extend[C]['地区'];H=A.extend[C]['年代'];I=A.extend[C]['简介'];J=A.extend[C]['主演'];K=A.extend[C]['导演'];L=A.extend[C]['标签'];D[F]=A.fun_css(B,E);D[V]=A.fun_css(B,G);D[U]=A.fun_css(B,H);D[Y]=A.fun_css(B,I);D[W]=A.fun_css(B,J);D[X]=A.fun_css(B,K);D[Q]=A.fun_css(B,L)
		try:g=J.get(c,headers=A.extend[P]);R=O(g.text.encode());d(R);e(R);f(R)
		except K as h:L(h)
		S[E].append(D);return S
	def searchContent(A,key,quick,page='1'):
		Q={E:[],I:0,M:0};B=A.extend[N]+A.extend['搜索url'].replace('@wd',key).replace(S,page)
		def T(doc_html):
			B='搜索数据';K=A.extend[B][R]
			for I in doc_html(K).items():J=A.extend[B][G].split(D);L=A.extend[B][F];M=A.extend[B][C];N=A.extend[B][H];Q[E].append({G:A.fun_re(A.fun_css(I,J[0]),J[1]),F:A.fun_css(I,L),C:A.fun_css(I,M),H:A.fun_css(I,N)})
		try:U=J.get(B,headers=A.extend[P]);V=O(U.text.encode());T(V)
		except K as W:L(W)
		return Q
	def playerContent(B,flag,pid,vipFlags):
		C='url';A={C:B.error_play_url,I:0,M:0,'header':{}};D=B.extend['播放数据']['嗅探播放']
		if D:A[I]=1;A[C]=pid
		return A
	def localProxy(A,params):0
	def fun_css(E,doc_html,rule):
		D=doc_html;A=rule
		if len(A)==0:return B
		C=A.split('@')
		if'@text'in A:return D(C[0]).text()
		return D(C[0]).attr(C[1])
	def fun_re(B,doc_html,rule):
		A=doc_html
		if re.search(rule,A):return re.search(rule,A).group(1)
		return A
if __name__=='__main__':0
