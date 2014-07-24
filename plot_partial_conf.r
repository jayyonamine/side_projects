library('ggplot2')
library('randomForest')
set.seed(2014)
 
rf_predict<-function(rf_object, data){
	if (rf_object$type=="classification"){
		p <-predict(rf_object, data, type="prob")
		p<-as.vector(p[,2])
	} else {
		p <-predict(rf_object, data)
	}
	return (p)
}
 
plot_partial<- 
    function(rf, X, dv, iv, conf_int_lb=.25, 
    	     conf_int_ub=.75, range_low=NULL, 
    	     range_high=NULL, delta=FALSE, num_sample=NULL)
{
	iv_name<-substitute(iv)
	dv_name<-substitute(dv)
	if (is.factor(X[, iv_name])==TRUE){
		factor_var<-unique(iris[, iv_name])
		#the test set needs all factor levels.  so, we build them and will drop them before we plot
		factor_names <- attributes(factor_var)$levels
		fix_factor_df<-data.frame(X[1:length(factor_names),])
        fix_factor_df[, iv_name]<-factor_names
		y_hat_df <- data.frame(matrix(vector(),0, 2))
		y_temp <- data.frame(matrix(vector(), nrow(X), 2))
		y<-predict(rf, X)
		for (i in 1:length(factor_names)){
			X[, iv_name] <- factor_names[i]
			X[, iv_name] <- factor(X[, iv_name])
			X_temp<-rbind(X, fix_factor_df)
			p<-rf_predict(rf, X_temp)
			y_temp[,1]<-p[1:nrow(X)] #drop the fix_factor_df rows
			if (delta==TRUE){
				y_temp[,1]<-y_temp[,1]-y
			}
			y_temp[,2]<-factor_names[i]
			y_hat_df<-rbind(y_hat_df, y_temp)
		}
		plot<- qplot(y_hat_df[,2], y_hat_df[,1], 
		    data = y_hat_df, 
		    geom="boxplot", 
		    main = paste("Partial Dependence of", (iv_name), "on", (dv_name))) +
	        ylab(bquote("Predicted values of" ~ .(dv_name))) +
	        xlab(iv_name)
	return (plot)
	} else {
		conf_int <-(conf_int_ub-conf_int_lb)*100
		temp<-sort(X[, iv_name])
		if (is.null(num_sample)==FALSE){
			temp<-sample(temp, num_sample)
		}
		if (is.null(range_low)==FALSE & is.null(range_high)==FALSE){
			low_value<-quantile(temp, range_low)
			high_value<-quantile(temp, range_high)
			temp<-temp[temp<high_value & temp>low_value]
		}
		y_hat_mean<-vector()
		y_hat_lb<-vector()
		y_hat_ub<-vector()
		y<-rf_predict(rf, X)
		for (i in 1:length(temp)){
			X[, iv_name] <- temp[i]
			y_hat<-rf_predict(rf, X)
			if (delta==TRUE){
				y_hat<-y_hat-y
			}
			y_hat_mean[i]<-weighted.mean(y_hat)
		    y_hat_lb[i]<-quantile(y_hat, conf_int_lb)
		    y_hat_ub[i]<-quantile(y_hat, conf_int_ub)
		}
		df_new<-as.data.frame(cbind(temp, y_hat_mean, y_hat_lb, y_hat_ub))
		plot<- ggplot(df_new, aes(temp)) + 
		    geom_line(aes(y=y_hat_mean), colour="blue") + 
		    geom_ribbon(aes(ymin=y_hat_lb, ymax=y_hat_ub), alpha=0.2) +
		    geom_rug(aes()) +
		    xlab(iv_name) +
		    ylab(bquote("Predicted values of" ~ .(dv_name))) +
		    ggtitle(paste("Partial Dependence of", (iv_name), "on", (dv_name), "\n with", (conf_int), "% Confidence Intervals"))
		return (plot)
	}
}
