import laspy 
import numpy as np
import matplotlib.pyplot as plt

#%%

las = laspy.read('Desktop\\2693_1262.las')


#%%
np.unique(las.classification)

las.header.point_count
las.header.z_max


# auflisten verfügbarer dimensionen. darunter:
    #classification (index 8)
    #xyz (indexe 0..2)
list(las.point_format.dimension_names)



#%% filtern nach classifications

len(las[las['classification']==1].xyz)


las_geb = las[las['classification']==6]

#geht nicht so weil xyz darf keine missing coords haben. ergo: alle andern 
#koordinaten einfach nan setzen?
las_geb_xyz=las_geb.xyz
# np.savetxt('Desktop\\test_geb.csv', las_geb_xyz, fmt='%.2f')

#%% plot 3d

X = las_geb_xyz[:10000,0]
Y = las_geb_xyz[:10000,1]
Z = las_geb_xyz[:10000,2]
 
fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d') 
# ax.plot_trisurf(X, Y, Z, color='white', 
#     edgecolors='grey', linewidth=0.2, alpha=0.5) 
ax.scatter(X, Y, Z, c='red', s=0.2) 
plt.show()




#%% versuch
# las_geb = las

# las_geb[las_geb.classification != 6].z = 0


x = las.x.scaled_array()
y = las.y.scaled_array()
z = las.z.scaled_array()
c = las.classification.array
i = las.intensity

lasnp = np.stack([x,y,z,c,i],axis=1)

lasnp_geb = lasnp.copy()

lasnp_geb[lasnp_geb[:,4]!= 6, 2] = -9999

#%% plot that too
# X = lasnp_geb[::10,0]
# Y = lasnp_geb[::10,1]
# Z = lasnp_geb[::10,2]

 
# fig = plt.figure() 
# ax = fig.add_subplot(111, projection='3d') 
# # ax.plot_trisurf(X, Y, Z, color='white', 
# #     edgecolors='grey', linewidth=0.2, alpha=0.5) 
# ax.scatter(X, Y, Z, c='red', s=0.2) 
# plt.show()




np.savetxt('Desktop\\test_geb.xyz', lasnp_geb[:10000,0:3], fmt='%.2f')




























