import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import math
import numpy as np
#import seaborn as sns
import matplotlib.colors as clr
import scipy.sparse.linalg

# For state a=(i_1,i_2,...,i_M), this function returns the "position" of this state in a list with all states lexicographically ordered. See Section 1.1 in Supplementary Material.
def Pos_R0(a,Ns,M,k):
	position=0
	for i in range(1,M+1):
		prod=1
		for h in range(i+1,M+1):
			if h!=k:
				prod=prod*(Ns[h-1]+1)
			else:
				prod=prod*Ns[h-1]
		if i!=k:	
			position+=a[i-1]*prod
		if i==k:
			position+=(a[i-1]-1)*prod
	return int(position)

# This is the construction of matrix D^{(j)} in Supplementary Material, Section 1.1
def Fill_Matrix_A(A,l,a,n,M,Ns,k,Gama,Betas,Lambdas):
	if l<M:
		if k==l:
			ini=1
		else:
			ini=0
		for il in range(ini,Ns[l-1]+1):
			a[l-1]=il
			Fill_Matrix_A(A,l+1,a,n,M,Ns,k,Gama,Betas,Lambdas)
			a[l-1]=ini
	else:
		if k==l:
			ini=1
		else:
			ini=0
		for il in range(ini,Ns[l-1]+1):
			a[l-1]=il
			
			denominator=delta
			for h in range(1,M+1):
				denominator+=a[h-1]*Gama[h-1]+(Ns[h-1]-a[h-1])*Lambdas[h-1]
				for p in range(1,M+1):
					denominator+=(Ns[h-1]-a[h-1])*a[p-1]*Betas[p-1,h-1]
				
			for h in range(1,M+1):
				if h!=k:
					if a[h-1]>0:
						new=np.append([],a)
						new[h-1]-=1
						A[Pos_R0(a,Ns,M,k),Pos_R0(tuple(new),Ns,M,k)]+=Gama[h-1]*a[h-1]/denominator
				else:
					if a[h-1]>0:
						new=np.append([],a)
						new[h-1]-=1
						A[Pos_R0(a,Ns,M,k),Pos_R0(tuple(new),Ns,M,k)]+=Gama[h-1]*(a[h-1]-1)/denominator
				if a[h-1]<Ns[h-1]:
					new=np.append([],a)
					new[h-1]+=1
					A[Pos_R0(a,Ns,M,k),Pos_R0(tuple(new),Ns,M,k)]+=Lambdas[h-1]*(Ns[h-1]-a[h-1])/denominator
					for p in range(1,M+1):
						if p!=k:
							A[Pos_R0(a,Ns,M,k),Pos_R0(tuple(new),Ns,M,k)]+=Betas[p-1,h-1]*a[p-1]*(Ns[h-1]-a[h-1])/denominator
						else:
							A[Pos_R0(a,Ns,M,k),Pos_R0(tuple(new),Ns,M,k)]+=Betas[p-1,h-1]*(a[p-1]-1)*(Ns[h-1]-a[h-1])/denominator
			a[l-1]=ini

# This function constructs vector e^{(j)}(n) in Supplementary Material, Section 1.1
def Fill_Vector_b(b,l,a,n,M,Ns,k,Gama,Betas,Lambdas,Xis):
	if l<M:
		if k==l:
			ini=1
		else:
			ini=0

		for il in range(ini,Ns[l-1]+1):
			a[l-1]=il
			Fill_Vector_b(b,l+1,a,n,M,Ns,k,Gama,Betas,Lambdas,Xis)
			a[l-1]=ini
	else:
		if k==l:
			ini=1
		else:
			ini=0

		for il in range(ini,Ns[l-1]+1):
			a[l-1]=il
			denominator=delta
			for h in range(1,M+1):
				denominator+=a[h-1]*Gama[h-1]+(Ns[h-1]-a[h-1])*Lambdas[h-1]
				for p in range(1,M+1):
					denominator+=(Ns[h-1]-a[h-1])*a[p-1]*Betas[p-1,h-1]
			if n>0:
				for h in range(1,M+1):
					if a[h-1]<Ns[h-1]:
						new=np.append([],a)
						new[h-1]+=1
						b[Pos_R0(a,Ns,M,k),0]+=Betas[k-1,h-1]*(Ns[h-1]-a[h-1])*Xis[n-1][0,Pos_R0(tuple(new),Ns,M,k)]/denominator
			else:
				b[Pos_R0(a,Ns,M,k),0]+=Gama[k-1]/denominator
				b[Pos_R0(a,Ns,M,k),0]+=delta/denominator
			a[l-1]=ini

# Case Study 5. 8 Patients, 4 AP1 HCWs, 2 AP2 HCWs and 1 Peripatetic HCW, according to contact network in Figure 13

N=2+2+2+2+1+1+1+1+1+1+1
M=11
Ns=[2,2,2,2,1,1,1,1,1,1,1]

# beta AP1
bAP1 = 0.35

# beta AP2
bAP2 = 0.12

# beta Peri
bPeri = 0.07

# HCW hand-washing rate
mu = 24.0

# Discharge rate
gamma = 0.1

# Global detection rate
delta=0

# This code computes the reproduction number of an AP2 HCW (AP2_1). Figure 15 middle

# Since AP2_1 HCW is at compartmental level 9, we set j=9. We are interested in computing R^{(j)}
j=9

# For initial state (0,...,0,1,0,...,0), where "1" corresponds to compartmental level j
init_state=[0]*M
init_state[j-1]=1

# This is the dimension of the system of equations to be solved. See Supplementary Material, Section 1.2
Num_States=1
for i in range(1,M+1):
	if i!=j:
		Num_States=Num_States*(Ns[i-1]+1)
	else:
		Num_States=Num_States*Ns[i-1]

# Since we are interested in computing the reproduction number R^{(j)}, we do not have any k.

# Since we can compute probabilities p(R^{(j)}=n), n=0,1,...., we can truncate the distribution so that total mass 0.9999 is accumulated
p_trunc=0.9999

precision=21

# The heatmap contains 21x21 values E[R^{(j)}], for different values of (beta_AP2,mu)
num_bAP2s=precision
num_mus=precision

bAP2s=[]
mus=[]

mean_R0_AP2=np.asmatrix(np.zeros((num_bAP2s,num_mus)))

for bAP2_index in range(num_bAP2s):
	print(bAP2_index)
	bAP2=0.1+bAP2_index*(0.15-0.1)/(num_bAP2s-1.0)
	bAP2s=np.append(bAP2s,bAP2)
	
	for mu_index in range(num_mus):
		print(mu_index)
		mu=1.0+mu_index*(24.0-1.0)/(num_mus-1.0)
		mus=np.append(mus,mu)

		# "Gama" vector contains rates \mu_j
		Gama=np.asmatrix(np.zeros((M,1)))

		Gama[0]=gamma
		Gama[1]=gamma
		Gama[2]=gamma
		Gama[3]=gamma
			
		Gama[4]=mu
		Gama[5]=mu
		Gama[6]=mu
		Gama[7]=mu

		Gama[8]=mu
		Gama[9]=mu

		Gama[10]=mu

		# "Betas" matrix contains rates \lambda_kj
		Betas=np.asmatrix(np.zeros((M,M)))

		Betas[0,4]=bAP1
		Betas[4,0]=bAP1

		Betas[1,5]=bAP1
		Betas[5,1]=bAP1

		Betas[2,6]=bAP1
		Betas[6,2]=bAP1

		Betas[3,7]=bAP1
		Betas[7,3]=bAP1
				
		Betas[0,8]=bAP2
		Betas[8,0]=bAP2
		Betas[1,8]=bAP2
		Betas[8,1]=bAP2

		Betas[2,9]=bAP2
		Betas[9,2]=bAP2
		Betas[3,9]=bAP2
		Betas[9,3]=bAP2

		Betas[0,10]=bPeri
		Betas[10,0]=bPeri

		Betas[1,10]=bPeri
		Betas[10,1]=bPeri

		Betas[2,10]=bPeri
		Betas[10,2]=bPeri

		Betas[3,10]=bPeri
		Betas[10,3]=bPeri

		# "Lambdas" vector contains rates \lambda_j
		Lambdas=np.asmatrix(np.zeros((M,1)))

		mean=0
		mean2=0

		suma=0

		Xis=[np.asmatrix(np.zeros((Num_States,1))) for n in range(501)]
		Identity=np.asmatrix(np.eye(Num_States))

		A=np.asmatrix(np.zeros((Num_States,Num_States)))

		a=[0]*M

		l=1
		if j==l:
			ini=1
		else:
			ini=0

		for il in range(ini,Ns[l-1]+1):
			a[l-1]=il
			Fill_Matrix_A(A,l+1,a,0,M,Ns,j,Gama,Betas,Lambdas)
			a[l-1]=ini

		n=-1
		while(suma<p_trunc and n<500):
			n+=1
			
			b=np.asmatrix(np.zeros((Num_States,1)))
			
			a=[0]*M
			
			l=1
			if j==l:
				ini=1
			else:
				ini=0

			for il in range(ini,Ns[l-1]+1):
				a[l-1]=il
				Fill_Vector_b(b,l+1,a,n,M,Ns,j,Gama,Betas,Lambdas,Xis)
				a[l-1]=ini

			Xis[n]=np.asmatrix(scipy.sparse.linalg.spsolve(Identity-A,b))
			
			suma+=Xis[n][0,Pos_R0(tuple(init_state),Ns,M,j)]
			mean+=n*Xis[n][0,Pos_R0(tuple(init_state),Ns,M,j)]
			mean2+=n*n*Xis[n][0,Pos_R0(tuple(init_state),Ns,M,j)]
			
			print(n,suma)
			
			if suma>p_trunc:
				break
		mean_R0_AP2[num_bAP2s-1-bAP2_index,mu_index]=mean

fig = plt.figure()
ax = fig.add_subplot(111)
cax = plt.imshow(mean_R0_AP2, cmap='hot', interpolation='nearest',extent=[mus[0],mus[num_mus-1],bAP2s[0],bAP2s[num_bAP2s-1]],aspect="auto")
barra = fig.colorbar(cax)
barra.set_label(r'$E[R_{(0,\dots,0,1,0,0)}^{(9)}(1)+R_{(0,\dots,0,1,0,0)}^{(9)}(2)]$', fontsize=15)

ax.set_xlabel(r'$\mu$', fontsize=15)
ax.set_ylabel(r'$\beta_{AP2}$', fontsize=15)

plt.savefig('Figure15_Middle.png')
